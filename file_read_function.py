import os
import re


def read_file(folder = 'questions'):
    # QUIZ_FOLDER = 'questions'
    question_and_answer = {}

    script_dir = os.path.dirname(os.path.abspath(__file__))
    questions_dir = os.path.join(script_dir, folder)

    for filename in os.listdir(questions_dir):
        if filename.endswith('txt'):
            with open(os.path.join(questions_dir, filename), 'r', encoding='KOI8-R') as f:
                file_contents = f.read()
            # print(file_contents.split('\n\n'))
            question = None
            answer = None
            for question_answer in file_contents.split('\n\n')[3:]:
                # print('-', q_n_a, end='')
                if question_answer.strip().startswith('Вопрос'):
                    question = re.split(r'Вопрос \d+:', question_answer.replace('\n', ' '))[1].strip()
                elif question_answer.strip().startswith('Ответ'):
                    answer = question_answer.replace('\n', ' ').strip('Ответ:').strip()
                if question and answer:
                    question_and_answer[question] = answer
                    answer = None
                    question = None
    return question_and_answer


if __name__ == '__main__':
    read_file()