import logging

import peewee

from app.codeforces_parsers import BSCodeforcesParser, APICodeforcesParser
from exc.exceptions import CodeforcesAPIRespException, CodeforcesUnexpectedAnswerException, CodeforcesConnectionError
from models import Problem, Tag, ProblemTags
from models import db
from settings import FOR_UPDATE_KEYS, NUMBER_KEY, TAGS_KEY


class CodeforcesDatabaseUpdater:

    def __init__(self):
        self.base_parser = APICodeforcesParser()
        self.spare_parser = BSCodeforcesParser()
        self.batch_size = 100

    def update(self):
        problems = self._get_problems()
        for_create, for_update = self._split_problems(problems)

        if for_create:
            Problem.bulk_create(for_create.keys(), batch_size=self.batch_size)
            problems_tags = []
            for problem, tags in for_create.items():
                problems_tags += [ProblemTags(problem=problem, tag=tag) for tag in tags]
            ProblemTags.bulk_create(problems_tags, batch_size=self.batch_size)

        if for_update:
            Problem.bulk_update(for_update.keys(), FOR_UPDATE_KEYS, batch_size=self.batch_size)
            for_create_problem_tags = self._split_problem_tags(for_update)
            ProblemTags.bulk_create(for_create_problem_tags, batch_size=self.batch_size)

    def _get_problems(self):
        for _ in range(3):
            try:
                problems = self._call_parser(self.base_parser)
                return problems
            except (CodeforcesAPIRespException, CodeforcesUnexpectedAnswerException, CodeforcesConnectionError) as exp:
                logging.exception(exp)

        return self._call_parser(self.spare_parser)

    @staticmethod
    def _call_parser(parser):
        return parser.get_problems()

    @staticmethod
    @db.atomic()
    def _split_problems(problems):
        for_create, for_update = {}, {}
        for problem in problems:
            tags = set()
            for tag in problem[TAGS_KEY]:
                db_tag, _ = Tag.get_or_create(name=tag)
                tags.add(db_tag)
            try:
                db_problem = Problem.get(number=problem[NUMBER_KEY])
            except peewee.DoesNotExist:
                db_problem = Problem(**problem)
                for_create[db_problem] = tags
            else:
                for_update[db_problem] = tags
                db_problem.name, db_problem.link, db_problem.prating, db_problem.solved_count = (problem[key] for key in
                                                                                                 FOR_UPDATE_KEYS)
        return for_create, for_update

    @staticmethod
    @db.atomic()
    def _split_problem_tags(for_update):
        for_create = []
        for problem, tags in for_update.items():
            for problem_tag in ProblemTags.select().where(ProblemTags.problem == problem):
                if problem_tag.tag not in tags:
                    problem_tag.delete()
                else:
                    tags.discard(problem_tag.tag)
            for tag in tags:
                for_create.append(ProblemTags(problem=problem, tag=tag))
        return for_create


if __name__ == '__main__':
    updater = CodeforcesDatabaseUpdater()
    updater.update()
