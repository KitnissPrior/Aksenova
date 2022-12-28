import csv
import requests
from datetime import timedelta, datetime
class HhDownloader:
    """Класс для представления загрузчика вакансий с HeadHunter

        Attributes:
            vacancies (list): строки с выгруженным данными о вакансиях
    """
    def __init__(self):
        """Инициализирует объект загрузчика данных по валютам
        """
        titles = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
        self.vacancies = []
        self.vacancies.append(titles)

    def add_vacancy_to_list(self, vacancy):
        """Добавляет даныне о вакансии в список

            Args:
                vacancy (dict): данные об одной вакансии
        """
        salary_from = ''
        salary_to = ''
        currency = ''
        salary = vacancy['salary']
        if salary:
            salary_from = salary['from']
            salary_to = salary['to']
            currency = salary['currency']

        self.vacancies.append([vacancy['name'], salary_from, salary_to, currency,
                               vacancy['area']['name'], vacancy['published_at']])

    def send_request_one_hour(self, start, end):
        """Отправляет запрос на получение 20 страниц с hh.ru в переданный временной диапазон
        и записывает полученные данные в список с вакансиями

            Args:
                start (str): начало временного диапазона (часы)
                end (str) : конец временного диапазона (часы)
        """
        for page in range(20):
            url = f"https://api.hh.ru/vacancies?specialization=1&per_page=100&page={page}" \
                f"&date_from=2022-12-15T{start}:00:00&date_to={'2022-12-15' if end != '00' else '2022-12-16'}T{end}:00:00"
            response = requests.get(url).json()
            for vacancy in response['items']:
                self.add_vacancy_to_list(vacancy)
    def add_vacancies_to_csv(self):
        """Добавляет вакансии в csv-файл
        """
        with open('hh_vacancies.csv', 'w', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator="\r")
            writer.writerows(self.vacancies)
    def get_data_from_hh_ru(self):
        """Получает данные с сайта hh.ru и сохраняет их в csv-файл"""
        start_hour = datetime(2022, 12, 15, 00, 00)
        last_hour = datetime(2022, 12, 16, 00, 00)

        while start_hour < last_hour:
            next_hour = start_hour + timedelta(hours=1)
            self.send_request_one_hour(
                datetime.strftime(start_hour,'%H'), datetime.strftime(next_hour,'%H'))
            start_hour = next_hour

        self.add_vacancies_to_csv()

hh_down = HhDownloader()
hh_down.get_data_from_hh_ru()