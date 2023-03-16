import telebot

from settings import BOT_TOKEN, BASE_URL
from models import Problem, ChatState, Tag, ProblemTags, Contest

bot = telebot.TeleBot(BOT_TOKEN)

CONTEST_DATA, PROBLEM_DATA, RATING_DATA = "c", "p", "r"

CONTEST_MESSAGE_SAMPLE = '[Задача №{number}]({link}) Название: {name}\n'


def get_start_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    contest_button = telebot.types.InlineKeyboardButton("Получить контест", callback_data=CONTEST_DATA)
    problem_button = telebot.types.InlineKeyboardButton("Узнать о задаче", callback_data=PROBLEM_DATA)
    markup.add(contest_button, problem_button)
    return markup


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = get_start_markup()
    bot.send_message(message.chat.id,
                     "Привет, я тестовый бот Codeforces. Я могу составить контест по заданным "
                     "параметрам, а также подробно рассказать о выбранной задаче по ее номеру.",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def button_message(call):
    markup = telebot.types.InlineKeyboardMarkup()
    if call.data == CONTEST_DATA:
        rating = Problem.select(Problem.rating).distinct()
        buttons = []
        for rtn in rating:
            button = telebot.types.InlineKeyboardButton(rtn.rating, callback_data=f'{RATING_DATA}:{rtn.rating}')
            buttons.append(button)
        markup.add(*buttons)
        bot.send_message(call.message.chat.id, 'Выберите сложность', reply_markup=markup)
    elif call.data == PROBLEM_DATA:
        bot.send_message(call.message.chat.id, 'Введите номер задачи')
    else:
        data_type, value = call.data.split(':')
        if data_type == RATING_DATA:
            ChatState.create(chat_id=call.message.chat.id, rating=int(value))
            tags = Tag.select()
            buttons = [telebot.types.InlineKeyboardButton(
                tag.name, callback_data=f'tag:{tag.id}'
            ) for tag in tags]
            markup.add(*buttons)
            bot.send_message(call.message.chat.id, 'Выберите тему', reply_markup=markup)
        else:
            state = ChatState.get(chat_id=call.message.chat.id)
            tag = Tag.get(id=value)
            query = (Problem
                     .select(Problem, ProblemTags.tag)
                     .join(ProblemTags)
                     .where(Problem.rating == state.rating, ProblemTags.tag == tag, Problem.contest == None)
                     .limit(10))
            contest = Contest().create()
            answer = ''
            for row in query:
                row.contest = contest
                answer += CONTEST_MESSAGE_SAMPLE.format(number=row.number, link=BASE_URL + row.link, name=row.name)
            Problem.bulk_update(query, ['contest'])
            markup = get_start_markup()
            bot.send_message(call.message.chat.id, answer, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: True)
def get_problem(message):
    markup = get_start_markup()
    problem = Problem.get_or_none(number=message.text)
    if problem:
        answer = f'[Задача №{problem.number}]({BASE_URL + problem.link})\n' \
                 f'Название: {problem.name}\n' \
                 f'Темы: {", ".join([tag.tag.name for tag in problem.tags])}\n' \
                 f'Сложность: {problem.rating}\n' \
                 f'Количество решивших: {problem.solved_count}'
        bot.send_message(message.chat.id, answer, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Задача не найдена', reply_markup=markup)
