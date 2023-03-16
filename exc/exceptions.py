import requests


class CodeforcesAPIRespException(KeyError):

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return f'Сервер ответил с ошибкой: {self.message}'


class CodeforcesUnexpectedAnswerException(Exception):

    def __str__(self) -> str:
        return 'Сервер отдал неожиданный ответ'


class CodeforcesUnexpectedTag(KeyError):

    def __init__(self, tag: str):
        self.tag = tag

    def __str__(self) -> str:
        return f'Неизвестный тег: {self.tag}'


class CodeforcesConnectionError(requests.exceptions.ConnectionError):

    def __str__(self) -> str:
        return 'Сервер не отвечает'
