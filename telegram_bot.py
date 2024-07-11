import os
import re
import random
import redis
import argparse

import logging
from dotenv import load_dotenv

from file_read_function import read_file

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
        # host='redis-19024.c327.europe-west1-2.gce.redns.redis-cloud.com',
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        username=os.getenv('REDIS_USERNAME'),
        password=os.getenv('REDIS_PASS'),
    )
    # res = r.set('foo', 'bar')
    # # print(res)
    # print(r.get('foo'))


    user = update.effective_user
    context.user_data['q_n_a'] = read_file(folder)
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

def main(folder) -> None:

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


if __name__ == '__main__':
    # read_file()
    parser = argparse.ArgumentParser(description='Telegram Bot')
    parser.add_argument('--folder', type=str, default='questions', help='Destination folder (default: questions)')
    args = parser.parse_args()
    folder = args.folder

    main(folder)
