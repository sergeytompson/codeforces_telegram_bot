import os

BASE_URL = 'https://codeforces.com'

ENG_RU_TAG_MAP = {
    'dp': 'дп',
    'bitmasks': 'битмаски',
    'data structures': 'структуры данных',
    'implementation': 'реализация',
    'binary search': 'бинарный поиск',
    'divide and conquer': 'разделяй и властвуй',
    'graphs': 'графы',
    'shortest paths': 'кратчайшие пути',
    'constructive algorithms': 'конструктив',
    'greedy': 'жадные алгоритмы',
    'brute force': 'перебор',
    'math': 'математика',
    'number theory': 'теория чисел',
    'two pointers': 'два указателя',
    'string suffix structures': 'строковые суфф. структуры',
    'strings': 'строки',
    'dsu': 'снм',
    'hashing': 'хэши',
    'trees': 'деревья',
    'sortings': 'сортировки',
    'dfs and similar': 'поиск в глубину и подобное',
    'meet-in-the-middle': 'meet-in-the-middle',
    'combinatorics': 'комбинаторика',
    'geometry': 'геометрия',
    'games': 'игры',
    'fft': 'бпф',
    'probabilities': 'теория вероятностей',
    'flows': 'потоки',
    'graph matchings': 'паросочетания',
    'interactive': 'интерактив',
    'chinese remainder theorem': 'китайская теорема об остатках',
    '*special': '*особая задача',
    'matrices': 'матрицы',
    'ternary search': 'тернарный поиск',
    'schedules': 'расписания',
    '2-sat': '2-sat',
    'expression parsing': 'разбор выражений'
}

# Ключи для словарей задач
NUMBER_KEY = "number"
NAME_KEY = "name"
LINK_KEY = "link"
TAGS_KEY = "tags"
RATING_KEY = "rating"
SOLVED_COUNT_KEY = "solved_count"

FOR_UPDATE_KEYS = (NAME_KEY, LINK_KEY, RATING_KEY, SOLVED_COUNT_KEY)

DB = os.environ.get('POSTGRES_DB', 'codeforces_bot')
DB_CONFIG = {
    'user': os.environ.get("POSTGRES_USER", 'postgres'),
    'password': os.environ.get("POSTGRES_PASSWORD", "postgrespassword"),
    'host': os.environ.get("POSTGRES_HOST", "localhost"),
    'port': os.environ.get("POSTGRES_PORT", "5432"),
}

BOT_TOKEN = os.environ.get("BOT_TOKEN", '6073958784:AAE4pKYTMLjkg_nwHWJU-G-jacvjF83z7TY')
