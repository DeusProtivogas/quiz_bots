import os
import random
import redis
import argparse

import vk_api

from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from file_read_function import read_file


def get_user_response(event, vk_api, q_n_a, redis_db):
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.DEFAULT)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Счет', color=VkKeyboardColor.DEFAULT)

    if event.text == "Сдаться":
        text = f'{q_n_a.get( redis_db.get( event.user_id ).decode("utf-8") )}'
        vk_api.messages.send(
            user_id=event.user_id,
            keyboard=keyboard.get_keyboard(),
            message=f'Правильный ответ - {text}',
            random_id=random.randint(1, 1000)
        )
        event.text = "Новый вопрос"
    if event.text == "Новый вопрос":

        question, answer = random.choice(list(q_n_a.items()))
        redis_db.set(event.user_id, question)

        vk_api.messages.send(
            user_id=event.user_id,
            keyboard=keyboard.get_keyboard(),
            message=f'{question}',
            random_id=random.randint(1,1000)
        )
    else:
        if q_n_a.get(
                redis_db.get(
                    event.user_id
                ).decode("utf-8")
        ).split('.')[0] == event.text:
            vk_api.messages.send(
                user_id=event.user_id,
                keyboard=keyboard.get_keyboard(),
                message=f'Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
                random_id=random.randint(1, 1000)
            )
        else:
            vk_api.messages.send(
                user_id=event.user_id,
                keyboard=keyboard.get_keyboard(),
                message=f'Неправильно… Попробуешь ещё раз?',
                random_id=random.randint(1, 1000)
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VK Bot')
    parser.add_argument('--folder', type=str, default='questions', help='Destination folder (default: questions)')
    args = parser.parse_args()
    folder = args.folder

    load_dotenv()
    telegram_token = os.getenv('VK_KEY')

    questions_and_answers = read_file(folder)

    redis_db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=os.getenv('REDIS_DB'),
        username=os.getenv('REDIS_USERNAME'),
        password=os.getenv('REDIS_PASS'),
    )

    vk_session = vk_api.VkApi(token=telegram_token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            get_user_response(event, vk, questions_and_answers, redis_db)
