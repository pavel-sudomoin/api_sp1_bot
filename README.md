# Спринт 8 для Yandex.Praktikum - Telegram-бот

## Описание проекта

Телеграм-бот периодически обращается к API сервиса Практикум.Домашка и узнаёт статус вашего домашнего задания - взято ли задание в ревью, проверено ли оно (провалено или принято).

Затем полученный статус дз отправляется в ваш Телеграм-чат.

Бот разработан в учебных целях для **Yandex.Praktikum**.

## Используемые технологии

* Python 3.8
* python-telegram-bot

## Установка

Для работы боту требуется файл *.env* со следующими переменными окружения

```
PRACTICUM_TOKEN=YOUR_PRACTICUM_TOKEN # Токен, полученный на платформе Яндекс.Практикум
TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN # Токен вашего бота, полученный через @BotFather
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID # Ваш Chat_id
```

## Авторы

* [Yandex.Praktikum](https://praktikum.yandex.ru/)

* [Судомоин Павел](https://github.com/pavel-sudomoin/)
