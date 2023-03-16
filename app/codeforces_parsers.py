import threading
from abc import ABC, abstractmethod
from threading import Thread

import bs4
import requests

from exc.exceptions import (CodeforcesAPIRespException,
                            CodeforcesUnexpectedAnswerException,
                            CodeforcesUnexpectedTag,
                            CodeforcesConnectionError)
import settings


class AbstractCodeforcesParser(ABC):
    """Абстрактный класс для наших парсеров"""

    @abstractmethod
    def get_problems(self) -> list:
        """Абстрактный метод, для парсинга задач"""


class BSCodeforcesParser(AbstractCodeforcesParser):
    """Парсер, использующий requests и beautifulsoap"""

    url = settings.BASE_URL + "/problemset/page/{page_number}?order=BY_SOLVED_DESC&locale=ru"

    def get_problems(self):
        problems = []

        html_page = self._get_page(1)
        last_page = html_page.find_all('span', {'class': 'page-index'})[-1]
        last_page_num = int(last_page['pageindex'])

        for i in range(1, last_page_num + 1):
            Thread(target=self._parse_page, args=(i, problems,)).start()
        while threading.active_count() > 1:
            continue
        return problems

    def _parse_page(self, page_num, problems):
        html_page = self._get_page(page_num)
        self._get_problems_from_page(html_page, problems)

    def _get_page(self, page_number):
        resp = requests.get(self.url.format(page_number=page_number))
        html_page = bs4.BeautifulSoup(resp.text, features='html.parser')
        return html_page

    def _get_problems_from_page(self, html_page, problems):
        table_rows = html_page.find_all('tr')
        for tr in table_rows:
            if tr.th:
                continue
            problems.append(self._get_params(tr))

    @staticmethod
    def _get_params(tr):
        number_tr_index = title_div_index = 1
        title_tr_index = topic_div_index = 3
        complexity_tr_index = 7
        solutions_tr_index = 9

        td = tr.contents[number_tr_index]
        a = td.a
        link = a['href']
        number = a.text.strip()
        td = tr.contents[title_tr_index]
        div = td.contents[title_div_index]
        a = div.a
        name = a.text.strip()
        div = td.contents[topic_div_index]
        tags = []
        for i in range(1, len(div), 2):
            a = div.contents[i]
            tags.append(a.text.strip())
        td = tr.contents[complexity_tr_index]
        rating = int(td.text.strip())
        td = tr.contents[solutions_tr_index]
        solved_count = td.text.strip()
        return {
            settings.NUMBER_KEY: number,
            settings.NAME_KEY: name,
            settings.LINK_KEY: link,
            settings.TAGS_KEY: tags,
            settings.RATING_KEY: rating,
            settings.SOLVED_COUNT_KEY: solved_count,
        }


class APICodeforcesParser(AbstractCodeforcesParser):
    """Парсер, использующий API codeforces.com"""

    url = settings.BASE_URL + '/api/problemset.problems?locale=ru'
    link_template = '/problemset/problem/{cont_id}/{index}'

    def get_problems(self):
        problems_json = self._get_json()

        problems = [self._get_problem(problem, problem_statistics) for problem, problem_statistics in
                    zip(problems_json['problems'], problems_json['problemStatistics'])]

        return problems

    def _get_json(self):
        try:
            resp = requests.get(self.url)
        except requests.exceptions.ConnectionError:
            raise CodeforcesConnectionError()

        try:
            json_resp = resp.json()
        except requests.exceptions.JSONDecodeError:
            raise CodeforcesUnexpectedAnswerException()

        try:
            problems_json = json_resp['result']
        except KeyError:
            raise CodeforcesAPIRespException(json_resp['comment'])
        else:
            return problems_json

    def _get_problem(self, problem, problem_statistics):
        cont_id, index = problem['contestId'], problem['index']
        number = str(cont_id) + index
        name = problem[settings.NAME_KEY]
        link = self.link_template.format(cont_id=cont_id, index=index)
        tags = []
        for tag in problem[settings.TAGS_KEY]:
            try:
                tags.append(settings.ENG_RU_TAG_MAP[tag])
            except KeyError:
                raise CodeforcesUnexpectedTag(tag)
        try:
            rating = problem[settings.RATING_KEY]
        except KeyError:
            rating = 0
        solved_count = problem_statistics['solvedCount']
        return {
            settings.NUMBER_KEY: number,
            settings.NAME_KEY: name,
            settings.LINK_KEY: link,
            settings.TAGS_KEY: tags,
            settings.RATING_KEY: rating,
            settings.SOLVED_COUNT_KEY: solved_count,
        }
