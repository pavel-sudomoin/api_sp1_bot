import os
import sys
import requests
import telegram
import time
import logging

from dotenv import load_dotenv


class WrongHomeworkData(Exception):
    pass


class OneLineExceptionFormatter(logging.Formatter):
    def format_exception(self, exc_info):
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
BASE_URL = 'https://praktikum.yandex.ru/api/user_api/{method}/'
HOMEWORK_STATUSES = {
    'rejected': 'К сожалению в работе нашлись ошибки.',
    'approved': 'Ревьюеру всё понравилось, '
                'можно приступать к следующему уроку.'
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

f_handler = logging.FileHandler(filename=f'{BASE_DIR}/output.log', mode='w')
f_handler.setFormatter(
    OneLineExceptionFormatter(
        fmt='%(asctime)s|%(name)s|%(levelname)s|%(message)s|',
        datefmt='%d.%m.%Y %H:%M:%S'
    )
)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        f_handler
    ]
)

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
        homework_status = homework.get(status_key)

        verdict = HOMEWORK_STATUSES.get(
            homework_status,
            f'Статус вашей работы: {homework_status}'
        )

        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except WrongHomeworkData as e:
        logging.exception(f'Получена некорректная информация о работе: {e}')
        raise


def get_homework_statuses(current_timestamp):
    current_timestamp = current_timestamp or int(time.time())
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            BASE_URL.format(method='homework_statuses'),
            params=params,
            headers=headers
        )
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
        logging.exception('Возникла ошибка при соединении с сервером')
        raise


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.info('Бот запущен')
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
                logging.exception(f'Бот упал с ошибкой: {e}')
                time.sleep(5)
                continue
        except KeyboardInterrupt:
            break

    logging.info('Бот отключён')


if __name__ == '__main__':
    main()
