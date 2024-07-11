# Боты викторины

В этом проекте созданы два бота для работы с викториной

## Ссылки

- **Бот в телеграме**: [Ссылка](https://t.me/quizbotpleasebot)
- **Бот в ВК**: [Ссылка](https://vk.com/im?sel=-226432288)

## Установка

### Пошагово

1. **Клонировать репозиторий**

    ```sh
    git clone https://github.com/DeusProtivogas/quiz_bots
    cd yourproject
    ```

2. **Создать виртуальное окружение**
    ```sh
    python -m venv venv
    ```

3. **Активировать виртуальное окружение**
        ```sh
        source venv/bin/activate
        ```

4. **Установить зависимости**

    ```sh
    pip install -r requirements.txt
    ```

### Переменные окружения

Необходимо создать файл '.env', в котором должны быть следующие переменные:
```
TELEGRAM_TOKEN=токен для бота в телеграме
VK_KEY=ключ для бота в вк
REDIS_HOST= адрес базы Redis
REDIS_PORT=порт Redis
REDIS_DB=база
REDIS_USERNAME
REDIS_PASS
```


### Запуск
Для запуска ботов, необходимо использовать соответственно :


```sh
python telegram_bot.py
``` 
```sh
python vk_bot.py
``` 

Возможно указать путь до своей папки с вопросами (по умолчанию используется папка `questions`, находящаяся в корне проекта)

Для этого используется аргумент `--folder`:

```sh
python telegram_bot.py --folder path
``` 
```sh
python vk_bot.py --folder path
``` 