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


class QuizBot:
    def __init__(self, folder, redis_config, telegram_token):
        self.questions_and_answers = read_file(folder)
        self.redis_db = redis.Redis(**redis_config)
        self.telegram_token = telegram_token
        self.updater = Updater(self.telegram_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.setup_handlers()

    def setup_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],

            states={
                CHOICE: [
                    MessageHandler(Filters.regex('Новый вопрос'), self.send_question),
                    MessageHandler(Filters.regex('Сдаться$'), self.surrender),
                ],
                NEW_QUESTION: [MessageHandler(Filters.regex('Новый вопрос'), self.send_question)],
                GIVE_UP: [MessageHandler(Filters.regex('Сдаться'), self.surrender)],
                CHECK_ANSWER: [
                    MessageHandler(Filters.regex('Новый вопрос'), self.send_question),
                    MessageHandler(Filters.regex('Сдаться'), self.surrender),
                    MessageHandler(Filters.text, self.check_answer)
                ],
            },

            fallbacks=[],
        )
        self.dispatcher.add_handler(conv_handler)

    def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD)
        update.message.reply_markdown_v2(
            fr'Привет, {user.mention_markdown_v2()}\!',
            reply_markup=reply_markup,
        )
        return CHOICE

    def send_question(self, update: Update, context: CallbackContext) -> None:
        question, answer = random.choice(list(self.questions_and_answers.items()))
        self.redis_db.set(update.effective_user.id, question)
        update.message.reply_text(text=f"{question}")
        return CHECK_ANSWER

    def check_answer(self, update: Update, context: CallbackContext) -> None:
        reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD)
        question = self.redis_db.get(update.effective_user.id).decode("utf-8")
        correct_answer = self.questions_and_answers.get(question).split('.')[0]
        if correct_answer == update.message.text:
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

    def surrender(self, update: Update, context: CallbackContext) -> None:
        reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD)
        question = self.redis_db.get(update.effective_user.id).decode("utf-8")
        correct_answer = self.questions_and_answers.get(question)
        update.message.reply_text(
            text=f"Правильный ответ - {correct_answer}",
            reply_markup=reply_markup,
        )
        self.send_question(update, context)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()


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

    redis_config = {
        'host': os.getenv('REDIS_HOST'),
        'port': os.getenv('REDIS_PORT'),
        'db': os.getenv('REDIS_DB'),
        'username': os.getenv('REDIS_USERNAME'),
        'password': os.getenv('REDIS_PASS')
    }

    telegram_token = os.getenv('TELEGRAM_TOKEN')

    bot = QuizBot(folder, redis_config, telegram_token)
    bot.run()
