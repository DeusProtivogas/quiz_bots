import os
import re
import random

import logging
from dotenv import load_dotenv

from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


logger = logging.getLogger(__name__)

custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Счет']]

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    context.user_data['q_n_a'] = read_file()
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )



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

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        text=f"{question}",
        reply_markup=reply_markup)




def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # dispatcher.add_handler(CommandHandler("new_question", send_question))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Новый вопрос$'), send_question))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


def read_file():
    QUIZ_FOLDER = 'questions/'

    question_and_answer = {}

    with open(QUIZ_FOLDER + '1vs1200.txt', 'r', encoding='KOI8-R') as f:
        file_contents = f.read()
    cntr = 1
    # print(file_contents.split('\n\n'))
    q = None
    a = None
    for q_n_a in file_contents.split('\n\n')[3:]:
        # print('-', q_n_a, end='')
        if q_n_a.strip().startswith('Вопрос'):
            q = re.split(r'Вопрос \d+:', q_n_a.replace('\n', ' '))[1]
            print('---', q)
            print(cntr)
            cntr += 1
        elif q_n_a.strip().startswith('Ответ'):
            a = q_n_a.replace('\n', ' ').strip('Ответ:')
            print('--', a)
        if q and a:
            question_and_answer[q] = a
            a = None
            q = None
    return question_and_answer


if __name__ == '__main__':
    # read_file()
    main()
