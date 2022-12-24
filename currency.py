from collections import Counter
from date_converter import convert_to_date
from dateutil import rrule
import xmltodict
import pandas as pd
import requests
import json

class Currency:
    """Представляет объект валюты

        Attributes:
            vacancies (list) : строки, считанные из файла с вакансиями
            index (int): индекс, под которым находится валюта в каждой считанной строке
    """
    def __init__(self, rows, index):
        """Инициализирует объект валюты

            Args:
                rows (list) : строки, считанные из файла с вакансиями
                index (int): индекс, под которым находится валюта в каждой считанной строке
        """
        self.vacancies = rows
        self.index = index

    def get_date_range(self, date_index):
        """Вычисляет диапазон дат: находит минимальную и максимальную дату в выгрузке

            Returns:
                tuple: (минимальная дата, максимальная дата)
        """
        dates = [convert_to_date(row[date_index]) for row in self.vacancies]
        return min(dates), max(dates)

    # frequency = Counter([row[self.index] for row in self.vacancies if row[self.index] != 'RUR'])

    def get_currency_frequency(self):
        """Получает частотность, с которой встречаются различные валюты

            Returns:
                collections.Counter: частотность, с которой встречаются валюты из выгрузки
        """
        return Counter([row[self.index] for row in self.vacancies if row[self.index] != 'RUR'])

    def select_most_frequent_currencies(self):
        """Выбирает вакансии, в которых валюта встречается чаще 5000 раз в выгрузке

            Returns:
                list: вакансии, в которых валюта встречается чаще 5000 раз в выгрузке
        """
        currencies = self.get_currency_frequency()
        frequent_currencies = [cur[0] for cur in currencies.items() if cur[1] > 5000]
        currencies_with_rub = frequent_currencies + ['RUR']
        res = [row for row in self.vacancies if row[self.index] in currencies_with_rub]
        return frequent_currencies, res

    def process_currencies(self, date_index):
        """Обрабатывает данные по валютам: выбирает из выгрузки вакансии с наибольшей
        частотностью валют и формирует файл с курсами валют по месяцам

            Args:
                date_index (int): индекс, под которым находится поле с датой в выгрузке
            Returns:
                list: вакансии с наибольшей частотностью валют
        """
        frequent_currencies, correct_rows = self.select_most_frequent_currencies()
        min_date, max_date = self.get_date_range(date_index)

        uploader = Uploader(min_date, max_date, frequent_currencies)
        uploader.copy_currencies_from_bank_to_csv()

        return correct_rows

class Uploader:
    """Класс для представления загрузчика данных по валютам, выгруженных с внешних источников

        Attributes:
            min_date (datetime.datetime): нижняя граница временного диапазона
            max_date (datetime.datetime): верхняя граница временного диапазона
            currency_names (list): список валют
            upload_dict (dict): словарь для данных выгрузки
    """
    def __init__(self, min_date, max_date, currency_list):
        """Инициализирует объект загрузчика данных по валютам

        Attributes:
            min_date (datetime.datetime): нижняя граница временного диапазона
            max_date (datetime.datetime): верхняя граница временного диапазона
            currency_list (list): список валют
        """
        self.min_date = min_date
        self.max_date = max_date
        self.currency_names = ['date'] + currency_list
        self.upload_dict = {item: [] for item in self.currency_names}

    def check_empty_fields(self, max_length):
        """Проверяет наличие пустых полей в выгрузке и,
        если таковые имеются, записывает в словарь для выгрузки строку с пробелом

            Args:
                max_length (int) : максимальная длина строки для данных по каждой валюте
        """
        empty_fields = [item[0] for item in self.upload_dict.items() if len(item[1]) < max_length]
        for key in empty_fields:
            self.upload_dict[key].append(' ')

    def upload_data(self, date):
        """Выгружает данные по валютам с сайта центробанка

            Args:
                date (datetime.datetime): дата, которой соответствуют значения валют
            Returns:
                dict: словарь с данными выгрузки по валютам в заданный период
        """
        str_date = date.strftime("%d/%m/%Y")
        url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={str_date}"
        response = requests.get(url).text
        json_text = json.dumps(xmltodict.parse(response))
        return eval(json_text)['ValCurs']['Valute']

    def add_data_to_dictionary(self, month_currency, date):
        """Добавляет выгруженные данные по валютам в словарь для выгрузки

            Args:
                month_currency (dict): данные по валютам за один месяц
                date (datetime.datetime): дата, за которую были выгружены данные
        """
        self.upload_dict['date'].append(date.strftime("%Y-%m"))
        max_length = 0
        for item in month_currency.items():
            self.upload_dict[item[0]].append(float(item[1].replace(',', '.')))
            length = len(self.upload_dict[item[0]])
            max_length = max(max_length, length)
        self.check_empty_fields(max_length)

    def copy_currencies_from_bank_to_csv(self):
        """Получает выгрузку по валютам с сайта центробанка и сохраняет в csv-файл"""

        for dt in rrule.rrule(rrule.MONTHLY, dtstart=self.min_date, until=self.max_date):
            currencies = self.upload_data(dt)
            month_currency = {cur['CharCode']: cur['Value'] for cur in currencies if cur['CharCode'] in self.currency_names}
            self.add_data_to_dictionary(month_currency, dt)

        frame = pd.DataFrame(self.upload_dict)
        frame.reset_index(drop=True, inplace=True)
        frame.to_csv('csv/currency.csv', sep=',', encoding='utf-8')

