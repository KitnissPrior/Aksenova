import re
import os
import math
import datetime
from datetime import datetime as module_dt
import prettytable
from prettytable import PrettyTable
import csv_reader as reader
import cProfile
from dateutil.parser import parse as dt_parser
import maya
import arrow

class DataSet:
    """Класс для представления набора данных статистики по вакансиям

    Attributes:
        file_name (str): имя файла, из которого считываются данные
        vacancies_objects (list): список вакансий
        connector (InputConnect): объект, отвечающий за формирование данных статистики

    """
    def __init__(self, file_name):
        """Инициализирует объект DataSet

           Args:
               file_name (str): имя файла, из которого считываются данные
        """
        self.file_name = file_name
        self.vacancies_objects = []
        self.connector = InputConnect(self)

    def create_vacancy(self, vacancy_dict):
        """Создает объект Vacancy

           Args:
               vacancy_dict (dict): данные об одной вакансии
           Returns:
               Vacancy: информация о вакансии в виде объекта Vacancy
        """
        name = vacancy_dict['name']
        experience = vacancy_dict['experience_id']
        description = vacancy_dict['description']
        area = vacancy_dict['area_name']
        employer = vacancy_dict['employer_name']
        skills = vacancy_dict['key_skills']
        premium = vacancy_dict['premium']
        published_at = vacancy_dict['published_at']

        salary = Salary(vacancy_dict['salary_from'], vacancy_dict['salary_to'],
                        vacancy_dict['salary_gross'], vacancy_dict['salary_currency'])

        vacancy = Vacancy(name, description, skills, experience,
                          premium, employer, salary, area, published_at)
        return vacancy

    def parse_csv(self, input_data):
        """Считывает данные из csv-файла,
        форматирует, сортирует и фильтрует полученные данные

           Args:
               input_data (dict): параметры фильтрации и сортировки
        """
        rows, titles = reader.csv_reader(self.file_name)
        self.vacancies_objects = reader.csv_filer(rows, titles, self.create_vacancy)
        if len(self.vacancies_objects) == 0:
            print('Нет данных')
            return

        if input_data['filter'][0] != '':
            self.vacancies_objects = self.connector.filter_data(
                input_data['filter'][0], input_data['filter'][1])
            if len(self.vacancies_objects) == 0:
                print('Ничего не найдено')
        if len(self.vacancies_objects) != 0:
            if input_data['sort_param'] != '':
                sort_param = self.connector.eng_naming[input_data['sort_param']]
                is_reversed = (input_data['reversed'] == 'Да')
                sorting_func = self.connector.get_sorting_func(sort_param)
                self.vacancies_objects.sort(key=sorting_func, reverse=is_reversed)

            table = self.connector.create_table(self.vacancies_objects, self.connector.rus_naming)
            self.connector.print_table(table, input_data['range'], input_data['columns'])

class Vacancy:
    """Класс для представления вакансии

       Attributes:
           name (str): название профессии
           description (str): описание профессии
           key_skills (str): ключевые навыки
           experience_id (str): опыт работы
           premium (str): является ли премиум-вакансией
           employer_name (str): работодатель
           salary (Salary): зарплата
           area_name (str): место работы
           published_at (str): дата публикации
    """
    def __init__(self, name, description, skills, experience,
                 premium, employer, salary, area, published_at):
        """Инициализирует объект Vacancy

           Args:
                name (str): название профессии
                description (str): описание профессии
                skills (str): ключевые навыки
                experience (str): опыт работы
                premium (str): является ли премиум-вакансией
                employer (str): работодатель
                salary (Salary): зарплата
                area (str): место работы
                published_at (str): дата публикации
        """
        self.name = name
        self.description = description
        self.key_skills = skills
        self.experience_id = experience
        self.premium = premium
        self.employer_name = employer
        self.salary = salary
        self.area_name = area
        self.published_at = published_at

class Salary:
    """Класс для представления зарплаты

       Attributes:
           salary_from (str or int or float) : нижняя граница вилки оклада
           salary_to (str or int or float): верхняя граница вилки оклада
           salary_gross (str or bool): указан ли оклад с вычетом налогов
           salary_currency (str): валюта оклада
    """
    def __init__(self, salary_from, salary_to, gross, currency):
        """Инициализирует объект Salary

           Args:
               salary_from (str or int or float) : нижняя граница вилки оклада
               salary_to (str or int or float): верхняя граница вилки оклада
               gross (str or bool): указан ли оклад с вычетом налогов
               currency (str): валюта оклада
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = gross
        self.salary_currency = currency

    currency_to_rub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }

    def convert_to_rub(self):
        """Вычисляет среднюю зарплату из вилки и переводит в рубли при помощи
        словаря currency_to_rub

           Returns:
               float: средняя зарплата в рублях
        >>> Salary(10,20,'True','KGS').convert_to_rub()
        11.4
        >>> Salary(10.2,40.2,'True','RUR').convert_to_rub()
        25.0
        """
        average_salary = (float(self.salary_to) + float(self.salary_from)) // 2
        return average_salary * self.currency_to_rub[self.salary_currency]

class InputConnect:
    """Класс для фильтрации, сортировки данных и представления данных в виде таблицы

       Attributes:
           data_set (DataSet): набор данных по вакансиям
    """
    def __init__(self, data_set):
        """Инициализирует объект InputConnect

           Args:
               data_set (DataSet): набор данных по вакансиям
        """
        self.data_set = data_set

    rus_naming = {
        'name': 'Название', 'description': 'Описание',
        'key_skills': 'Навыки', 'experience_id': 'Опыт работы',
        'premium': 'Премиум-вакансия', 'employer_name': 'Компания',
        'salary': 'Оклад', 'area_name': 'Название региона',
        'published_at': 'Дата публикации вакансии'}

    eng_naming = {
        'Название': 'name', 'Описание': 'description',
        'Навыки': 'key_skills', 'Опыт работы': 'experience_id',
        'Премиум-вакансия': 'premium', 'Компания': 'employer_name',
        'Оклад': 'salary', 'Название региона': 'area_name',
        'Дата публикации вакансии': 'published_at',
        'Идентификатор валюты оклада': 'salary_currency'}

    experience_naming = {
        'noExperience': 'Нет опыта',
        'between1And3': 'От 1 года до 3 лет',
        'between3And6': 'От 3 до 6 лет',
        'moreThan6': 'Более 6 лет',
        'Нет опыта': 'noExperience',
        'От 1 года до 3 лет': 'between1And3',
        'От 3 до 6 лет': 'between3And6',
        'Более 6 лет': 'moreThan6'}

    experience_priority = {
        'noExperience': 0,
        'between1And3': 1,
        'between3And6': 2,
        'moreThan6': 3}

    bool_naming = {
        'Да': 'True',
        'Нет': 'False'}

    currency_naming = {
        'AZN': 'Манаты', 'BYR': 'Белорусские рубли', 'EUR': 'Евро',
        'GEL': 'Грузинский лари', 'KGS': 'Киргизский сом',
        'KZT': 'Тенге', 'RUR': 'Рубли', 'UAH': 'Гривны',
        'USD': 'Доллары', 'UZS': 'Узбекский сум',
        'Манаты': 'AZN', 'Белорусские рубли': 'BYR',
        'Евро': 'EUR', 'Грузинский лари': 'GEL',
        'Киргизский сом': 'KGS', 'Тенге': 'KZT', 'Рубли': 'RUR',
        'Гривны': 'UAH', 'Доллары': 'USD', 'Узбекский сум': 'UZS'}

    def profile(func):
        """Профилизатор"""
        def wrapper(*args, **kwargs):
            profile_filename = func.__name__ + '.prof'
            profiler = cProfile.Profile()
            result = profiler.runcall(func, *args, **kwargs)
            profiler.dump_stats(profile_filename)
            return result
        return wrapper

    '''
    def make_date_format_strptime(self, str_date):
        parts = str_date.split('T')
        time = parts[1]
        operation = time[8]

        delta = datetime.timedelta(hours=int(time[9:11]), minutes=int(time[11::]))
        date = module_dt.strptime(f"{parts[0]} {time[0:8]}", "%Y-%m-%d %H:%M:%S")

        return date + delta if operation == '+' else date - delta

    def make_date_format_arrow(self, str_date):
        date = arrow.get(str_date)
        parts = str_date.split('T')
        time = parts[1]
        operation = time[8]
        delta = datetime.timedelta(hours=int(time[9:11]), minutes=int(time[11::]))

        return date + delta if operation == '+' else date - delta
    
    def make_date_format_maya(self, str_date):
        date = maya.parse(str_date).datetime()

        parts = str_date.split('T')
        time = parts[1]
        operation = time[8]
        delta = datetime.timedelta(hours=int(time[9:11]), minutes=int(time[11::]))

        return date + delta if operation == '+' else date - delta
    '''

    @profile
    def make_date_format_util_parser(self, str_date):
        """Преобразует дату и время из строки в формат даты-времени с помощью
        утилиты dateutil.parser

        Args:
            str_date (str): дата и время
        Returns:
             datetime.datetime: дата и время с учетом часового пояса
        """
        date = dt_parser(str_date, ignoretz=True)

        parts = str_date.split('T')
        time = parts[1]
        operation = time[8]
        delta = datetime.timedelta(hours=int(time[9:11]), minutes=int(time[11::]))

        return date + delta if operation == '+' else date - delta

    def sort_by_date(self, vacancy):
        """Сортирует вакансии по дате публикации вакансии

           Args:
               vacancy (Vacancy): вакансия
           Returns:
               datetime: дата публикации вакансии
        """
        return self.make_date_format_util_parser(vacancy.published_at)

    def sort_by_skills(self, vacancy):
        """Сортирует вакансии по количеству навыков

           Args:
               vacancy (Vacancy): вакансия
           Returns:
               int: количество навыков у данной вакансии
        """
        if isinstance(vacancy.key_skills, str):
            return 1
        return len(vacancy.key_skills)

    def sort_by_experience(self, vacancy):
        """Сортирует вакансии по опыту работы с помощью словаря experience_priority

           Args:
               vacancy (Vacancy): вакансия
           Returns:
               int: приоритет опыта работы текущей вакансии
        """
        return self.experience_priority[vacancy.experience_id]

    def get_sorting_func(self, param):
        """Получает функцию сортировки

           Args:
               param (str): параметр сортировки
            Returns:
                def: функция сортировки списка вакансий
        """
        sorting_methods = {
            'salary': lambda vac: vac.salary.convert_to_rub(),
            'experience_id': self.sort_by_experience,
            'key_skills': self.sort_by_skills,
            'published_at': self.sort_by_date,
        }

        if param in sorting_methods.keys():
            return sorting_methods[param]
        return lambda vac: vac.__dict__[param]

    def modify_number(self, number):
        """Форматирует число: конвертирует в строку и,
        если у числа больше трех цифр, отделяет тысячи от сотен пробелом

           Args:
               number(int or float or str): число
           Returns:
               str: отформатированное число
        """
        number = str(math.floor(float(number)))
        length = len(number)
        if length > 3:
            number = f"{number[0:length - 3]} {number[length - 3::]}"
        return number

    """Возвращает одно значение из двух (val1, val2) 
    в зависимости от аргумента х(str): истина или ложь    
    """
    set_value = lambda self, x, val1, val2: val1 if x == 'True' else val2

    def formatter(self, vac):
        """Форматирует свойства вакансии для записи в таблицу

        Args:
            vac (Vacancy): вакансия
        Returns:
            Vacancy: вакансия с отформатированными свойствами
        """
        vac.experience_id = self.experience_naming[vac.experience_id]
        vac.premium = self.set_value(vac.premium, "Да", "Нет")

        salary_from = self.modify_number(vac.salary.salary_from)
        salary_to = self.modify_number(vac.salary.salary_to)
        taxes = self.set_value(vac.salary.salary_gross, 'Без вычета налогов', 'С вычетом налогов')
        currency = self.currency_naming[vac.salary.salary_currency]

        vac.salary = f"{salary_from} - {salary_to} ({currency}) ({taxes})"

        date = vac.published_at.split('-')
        day = str(date[2])[0:2]
        vac.published_at = f"{day}.{date[1]}.{date[0]}"
        return vac

    text_fields = ['name', 'description', 'employer_name', 'area_name',
                   'premium', 'experience_id']

    def filter_by_salary(self, value):
        """Фильтрует список вакансий по заданному значению оклада

           Args:
               value (str): заданный оклад
           Returns:
               list: список вакансий, в которых заданное значение оклада попадает
               в промежуток вилки оклада
        """
        return list(filter(lambda vac:
                           float(vac.salary.salary_from) <= float(value) <= float(vac.salary.salary_to),
                           self.data_set.vacancies_objects))

    def filter_by_skills(self, value):
        """Фильтрует вакансии по заданным навыкам

           Args:
               value (str): навыки
           Returns:
               list: список вакансий, среди навыков которых присутствуют заданные навыки
        """
        skills = value.split(', ')
        return list(filter(
            lambda vac: all(skill in vac.key_skills for skill in skills),
            self.data_set.vacancies_objects))

    def filter_by_date(self, value):
        """Фильтрует список вакансий по заданной дате публикации

           Args:
               value (str): дата публикации
           Returns:
               list: список вакансий с заданной датой публикации
        """
        value = value.split('.')
        date = f"{value[2]}-{value[1]}-{value[0]}"
        return list(filter(lambda vac: vac.published_at[0:10] == date,
                           self.data_set.vacancies_objects))

    def filter_by_currency(self, value):
        """Фильтрует список с вакансиями по валюте оклада

           Args:
               value (str): валюта оклада
           Returns:
               list: список вакансий с заданной валютой оклада
        """
        return list(filter(lambda vac: vac.salary.salary_currency == value,
                           self.data_set.vacancies_objects))

    filter_methods = {
        'salary': filter_by_salary,
        'key_skills': filter_by_skills,
        'published_at': filter_by_date,
        'salary_currency': filter_by_currency
    }

    def filter_data(self, param, value):
        """Фильтрует список вакансий в зависимости от заданного значения

           Args:
               param (str): параметр фильтрации - название свойства Vacancy
               value (str or float or int): значение, по которому будет осуществляться фильтрация
            Returns:
                list: отфильтрованный список вакансий
        """
        if param in self.text_fields:
            return list(filter(lambda vac: vac.__dict__[param] == value,
                               self.data_set.vacancies_objects))
        return self.filter_methods[param](self, value)

    def create_table(self, data_vacancies, dic_naming):
        """Создает таблицу с вакансиями

           Args:
               data_vacancies (list): список вакансий
               dic_naming (dict): названия столбцов таблицы
           Returns:
               PrettyTable: таблица с вакансиями
        """
        table = PrettyTable()
        table.hrules = prettytable.ALL
        table.align = "l"
        for title in dic_naming.values():
            table._max_width[title] = 20
        table.field_names = ['№'] + list(dic_naming.values())

        n = 0
        for vacancy in data_vacancies:
            vacancy = self.formatter(vacancy)
            n += 1
            for field in vacancy.__dict__.keys():
                attr = vacancy.__dict__[field]
                if field == 'key_skills' and isinstance(attr, list) and len(attr) > 1:
                    vacancy.__dict__[field] = '\n'.join(attr)
                if len(vacancy.__dict__[field]) > 100:
                    vacancy.__dict__[field] = vacancy.__dict__[field][0:100] + "..."
            table.add_row([n] + list(vacancy.__dict__.values()))
        return table

    def print_table(self, table, numbers, columns):
        """Выводит таблицу с вакансиями в консоль

           Args:
               table (PrettyTable): таблица с вакансиями
               numbers (list): номера строк таблицы, которые нужно вывести
               columns (list): названия столбцов таблицы, которые нужно вывести
        """
        names = table.field_names
        start_num = 0
        end_num = len(table.rows)
        if numbers[0] != '':
            start_num = int(numbers[0]) - 1
        if len(numbers) == 2 and int(numbers[1]) < end_num:
            end_num = int(numbers[1]) - 1
        if columns[0] != '':
            names = ['№'] + columns
        print(table.get_string(start=start_num, end=end_num, fields=names))

    def translate_paramater(self, title, value):
        """Переводит параметр сортировки или фильтрации
        с русского на английский язык при помощи словарей
        eng_namimg, experience_naming, currency_naming и bool_naming

           Args:
               title (str): название столбца, по которому
               будет производиться фильтрация или сортировка
               value (str): значение столбца title, по которому
               будет производиться фильтрация или сортировка
           Returns:
               tuple: (название столбца на английском, значение столбца на английском)
        """
        if re.search(r'[а-яА-Я]', title):
            title = self.eng_naming[title]

        if re.search(r'[а-яА-Я]', value):
            if value in self.experience_naming.keys():
                value = self.experience_naming[value]
            if value in self.currency_naming.keys():
                value = self.currency_naming[value]
            if value in self.bool_naming.keys():
                value = self.bool_naming[value]

        return title, value

    def check_filter_param(self, parameter):
        """Проверяет параметр фильтрации на корректность

           Args:
               parameter (str): параметр фильтрации
           Returns:
               bool: истина, если параметр корректен
               str: сообщение об ошибке, если параметр некорректен
        """
        if parameter == '':
            return True
        if ': ' not in parameter:
            return 'Формат ввода некорректен'

        parameter = parameter.split(': ')
        param_title = parameter[0]
        if (param_title not in self.rus_naming.keys() and
                param_title not in self.eng_naming.keys()):
            return 'Параметр поиска некорректен'

    def check_if_correct(self, value, correct_values):
        """Проверяет введенный параметр на корректность

           Args:
               value (str): значение введенного параметра
               correct_values (dict): словарь с корректными параметрами
           Returns:
               bool: истина, если параметр есть среди корректных значений или параметр пустой;
               в противном случае ложь
        """
        return value in correct_values.keys() or value == ''

    def check_input_values(self, filter_param, sort_param, is_reversed):
        """Проверяет корректность введенных значений

           Args:
               filter_param (str): параметр фильтрации
               sort_param (str): параметр сортировки
               is_reversed (str): нужно ли выполнять сортировку по убыванию
           Returns:
               str: сообщение об ошибке, если хотя бы одно из переданных значений введено некорректно;
               в противном случае возвращается пустая строка
        """
        result = self.check_filter_param(filter_param)
        error_message = f"{result}\n" if isinstance(result, str) else ''

        if not self.check_if_correct(sort_param, self.eng_naming):
            error_message += 'Параметр сортировки некорректен\n'

        if not self.check_if_correct(is_reversed, self.bool_naming):
            error_message += 'Порядок сортировки задан некорректно'

        if error_message != '' and error_message[len(error_message) - 1] == 'n':
            error_message[::2]
        return error_message

    def print_result(self, data_set, filter_param, sort_param, is_reversed, nums, columns):
        """Подготавливает параметры таблицы к печати и печатает таблицу с вакансиями

           Args:
               data_set (DataSet): набор данных о вакансиях
               filter_param (str): параметр фильтрации
               sort_param (str): параметр сортировки
               is_reversed (str): нужно ли выполнять обратную сортировку
               nums (list): номера строк, которые нужно напечатать
               columns (list): названия столбцов, которые нужно напечатать
        """
        filter_name = ''
        filter_value = ''
        if filter_param != '':
            parts = filter_param.split(': ')
            filter_name, filter_value = self.translate_paramater(parts[0], parts[1])

        input_data = {'filter': [filter_name, filter_value],
                      'sort_param': sort_param,
                      'reversed': is_reversed,
                      'range': nums,
                      'columns': columns}
        data_set.parse_csv(input_data)

def get_vacancies_table():
    """Выводит таблицу с вакансиями в зависимости от введенных параметров печати"""
    file_name = input('Введите название файла: ')
    data_set = DataSet(file_name)

    filter_param = input('Введите параметр фильтрации: ')
    sort_param = input('Введите параметр сортировки: ')
    is_reversed = input('Обратный порядок сортировки (Да / Нет): ')
    numbers = input('Введите диапазон вывода: ').split(' ')
    columns = input('Введите требуемые столбцы: ').split(', ')

    error_message = data_set.connector.check_input_values(
        filter_param, sort_param, is_reversed)

    if error_message != '':
        print(error_message)
        return False
    if os.stat(file_name).st_size == 0:
        print('Пустой файл')
        return False
    if error_message == '':
        data_set.connector.print_result(data_set, filter_param, sort_param, is_reversed, numbers, columns)
        return True
