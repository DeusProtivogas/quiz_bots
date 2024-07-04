import re


def read_file():
    QUIZ_FOLDER = 'questions/'

    question_and_answer = {}

    with open(QUIZ_FOLDER + '1vs1200.txt', 'r', encoding='KOI8-R') as f:
        file_contents = f.read()
    # cntr = 1
    # print(file_contents.split('\n\n'))
    q = None
    a = None
    for q_n_a in file_contents.split('\n\n')[3:]:
        # print('-', q_n_a, end='')
        if q_n_a.strip().startswith('Вопрос'):
            q = re.split(r'Вопрос \d+:', q_n_a.replace('\n', ' '))[1].strip()
            # print('---', q)
            # print(cntr)
            # cntr += 1
        elif q_n_a.strip().startswith('Ответ'):
            a = q_n_a.replace('\n', ' ').strip('Ответ:').strip()
            # print('--', a)
        if q and a:
            question_and_answer[q] = a
            a = None
            q = None
    return question_and_answer