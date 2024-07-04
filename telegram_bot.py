import os
import re
import random
import redis

import logging
from dotenv import load_dotenv

from utilities import read_file

from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

logger = logging.getLogger(__name__)

custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Счет']]



# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    redis_db = redis.Redis(
        host='redis-19024.c327.europe-west1-2.gce.redns.redis-cloud.com',
        port=19024,
        db=0,
        username="default",
        password='svHiq6auo7fXWuqGBzRIxVHEZQrRcfVS'
    )
    # res = r.set('foo', 'bar')
    # # print(res)
    # print(r.get('foo'))


    user = update.effective_user
    context.user_data['q_n_a'] = read_file()
    context.user_data['redis_db'] = redis_db
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )
    return CHOICE



def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def send_question(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    question, answer = random.choice(list(context.user_data['q_n_a'].items()))
    print(question, answer)

    # update.message.reply_markdown_v2(
    #     fr'Hi {user.mention_markdown_v2()}\!',
    #     reply_markup=ForceReply(selective=True),
    # )

    context.user_data['redis_db'].set( update.effective_user.id, question )

    print('1 ', context.user_data['redis_db'].get( update.effective_user.id ).decode("utf-8"))
    print('2 ', context.user_data['q_n_a'].get( context.user_data['redis_db'].get( update.effective_user.id ).decode("utf-8") ))

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        text=f"{question}",
        # reply_markup=ReplyKeyboardRemove(),
    )
    return CHECK_ANSWER


def check_answer(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    print('Ans', update.message.text)
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    if context.user_data['q_n_a'].get(
            context.user_data['redis_db'].get(
                update.effective_user.id
            ).decode("utf-8")
    ).split('.')[0] == update.message.text:
        update.message.reply_text(
            text=f"Поздравляю! Для следующего вопроса нажми «Новый вопрос»",
            reply_markup=reply_markup,
        )
    else:
        update.message.reply_text(
            text=f"Неправильно… Попробуешь ещё раз?",
            reply_markup=reply_markup,
        )
    return CHOICE

def surrender(update: Update, context: CallbackContext) -> None:

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        text=f"Правильный ответ - {context.user_data['q_n_a'].get( context.user_data['redis_db'].get( update.effective_user.id ).decode('utf-8') )}",

        reply_markup=reply_markup,
    )
    send_question(update, context)
    # return NEW_QUESTION

NEW_QUESTION, SHOW_SCORE, GIVE_UP, CHECK_ANSWER, CHOICE = range(5)

def main() -> None:

    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        states={
            CHOICE: [
                MessageHandler(Filters.regex('Новый вопрос'), send_question),
                # MessageHandler(Filters.regex('Счет'), send_question),
                MessageHandler(Filters.regex('Сдаться$'), surrender),
            ],
            NEW_QUESTION: [MessageHandler(Filters.regex('Новый вопрос'), send_question)],
            # SHOW_SCORE: [MessageHandler(Filters.regex('Счет'), send_question)],
            GIVE_UP: [MessageHandler(Filters.regex('Сдаться'), surrender)],
            CHECK_ANSWER: [
                MessageHandler(Filters.regex('Новый вопрос'), send_question),
                MessageHandler(Filters.regex('Сдаться'), surrender),
                MessageHandler(Filters.text, check_answer)
            ],
        },

        fallbacks=[],
    )
    dispatcher.add_handler(conv_handler)

    # on different commands - answer in Telegram
    # dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # dispatcher.add_handler(CommandHandler("new_question", send_question))
    # dispatcher.add_handler(MessageHandler(Filters.regex('^Новый вопрос$'), send_question))

    # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, check_answer))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

#
# def read_file():
#     QUIZ_FOLDER = 'questions/'
#
#     question_and_answer = {}
#
#     with open(QUIZ_FOLDER + '1vs1200.txt', 'r', encoding='KOI8-R') as f:
#         file_contents = f.read()
#     cntr = 1
#     # print(file_contents.split('\n\n'))
#     q = None
#     a = None
#     for q_n_a in file_contents.split('\n\n')[3:]:
#         # print('-', q_n_a, end='')
#         if q_n_a.strip().startswith('Вопрос'):
#             q = re.split(r'Вопрос \d+:', q_n_a.replace('\n', ' '))[1].strip()
#             print('---', q)
#             print(cntr)
#             cntr += 1
#         elif q_n_a.strip().startswith('Ответ'):
#             a = q_n_a.replace('\n', ' ').strip('Ответ:').strip()
#             print('--', a)
#         if q and a:
#             question_and_answer[q] = a
#             a = None
#             q = None
#     return question_and_answer


if __name__ == '__main__':
    # read_file()
    main()
