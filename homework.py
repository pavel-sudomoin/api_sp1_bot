import os
import requests
import telegram
import time
import logging

from dotenv import load_dotenv


class WrongHomeworkData(Exception):
    pass


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super(
            OneLineExceptionFormatter, self
        ).formatException(exc_info)
        return repr(result)

    def format(self, record):
        s = super(
            OneLineExceptionFormatter, self
        ).format(record)
        if record.exc_text:
            s = s.replace('\n', '') + '|'
        return s


load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(filename='file.log', mode='w')
c_format = logging.Formatter('%(message)s')
f_format = OneLineExceptionFormatter(
    fmt='%(asctime)s|%(name)s|%(levelname)s|%(message)s|',
    datefmt='%d.%m.%Y %H:%M:%S'
)
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
logger.addHandler(c_handler)
logger.addHandler(f_handler)

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    try:
        homework_name_key = 'homework_name'
        status_key = 'status'

        if homework_name_key not in homework:
            raise WrongHomeworkData('Сервер не передал имя работы.')
        if status_key not in homework:
            raise WrongHomeworkData('Сервер не передал статус работы.')

        homework_name = homework.get(homework_name_key)

        if homework.get(status_key) != 'approved':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = ("Ревьюеру всё понравилось, "
                       "можно приступать к следующему уроку.")

        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except WrongHomeworkData as e:
        logger.exception(f'Получена некорректная информация о работе: {e}')
        raise


def get_homework_statuses(current_timestamp):
    try:
        int(current_timestamp)
        params = {'from_date': current_timestamp}
        headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            params=params,
            headers=headers
        )
        return homework_statuses.json()
    except ValueError:
        logger.exception('Значение from_date не является целым числом')
        raise
    except requests.exceptions.RequestException as e:
        logger.exception('Возникла ошибка при соединении с сервером')
        raise


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    logger.info('Бот запущен')
    current_timestamp = int(time.time())

    while True:
        try:
            try:
                new_homework = get_homework_statuses(current_timestamp)
                if new_homework.get('homeworks'):
                    send_message(
                        parse_homework_status(new_homework.get('homeworks')[0])
                    )
                current_timestamp = new_homework.get('current_date')
                time.sleep(1200)
            except Exception as e:
                logger.exception(f'Бот упал с ошибкой: {e}')
                time.sleep(5)
                continue
        except KeyboardInterrupt:
            break

    logger.info('Бот отключён')


if __name__ == '__main__':
    main()
