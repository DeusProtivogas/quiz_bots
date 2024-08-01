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

NEW_QUESTION, SHOW_SCORE, GIVE_UP, CHECK_ANSWER, CHOICE = range(5)

logger = logging.getLogger(__name__)

CUSTOM_KEYBOARD = [['Новый вопрос', 'Сдаться'],
                   ['Счет']]



def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD)



    update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )
    return CHOICE

def send_question(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    question, answer = random.choice(list(questions_and_answers.items()))

    redis_db.set( update.effective_user.id, question )

    update.message.reply_text(
        text=f"{question}",
    )
    return CHECK_ANSWER


def check_answer(update: Update, context: CallbackContext) -> None:
    reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD)
    if questions_and_answers.get(
            redis_db.get(
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

    reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD)
    update.message.reply_text(
        text=f"Правильный ответ - {questions_and_answers.get( redis_db.get( update.effective_user.id ).decode('utf-8') )}",

        reply_markup=reply_markup,
    )
    send_question(update, context)



if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    parser = argparse.ArgumentParser(description='Telegram Bot')
    parser.add_argument('--folder', type=str, default='questions', help='Destination folder (default: questions)')
    args = parser.parse_args()
    folder = args.folder

    questions_and_answers = read_file(folder)

    redis_db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        username=os.getenv('REDIS_USERNAME'),
        password=os.getenv('REDIS_PASS'),
    )

    telegram_token = os.getenv('TELEGRAM_TOKEN')

    updater = Updater(telegram_token, use_context=True)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        states={
            CHOICE: [
                MessageHandler(Filters.regex('Новый вопрос'), send_question),
                MessageHandler(Filters.regex('Сдаться$'), surrender),
            ],
            NEW_QUESTION: [MessageHandler(Filters.regex('Новый вопрос'), send_question)],
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

    updater.start_polling()

    updater.idle()
