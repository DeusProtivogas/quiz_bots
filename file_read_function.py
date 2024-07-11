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
            cntr = 1
            # print(file_contents.split('\n\n'))
            q = None
            a = None
            for q_n_a in file_contents.split('\n\n')[3:]:
                # print('-', q_n_a, end='')
                if q_n_a.strip().startswith('Вопрос'):
                    q = re.split(r'Вопрос \d+:', q_n_a.replace('\n', ' '))[1].strip()
                    # print('---', q)
                    # print(cntr)
                    cntr += 1
                elif q_n_a.strip().startswith('Ответ'):
                    a = q_n_a.replace('\n', ' ').strip('Ответ:').strip()
                    # print('--', a)
                if q and a:
                    question_and_answer[q] = a
                    a = None
                    q = None
    return question_and_answer


if __name__ == '__main__':
    read_file()