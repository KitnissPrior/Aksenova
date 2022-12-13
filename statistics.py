import math
import csv_reader as reader
import doctest

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

    def create_vacancy(self, vac_dict):
        """Создает объект Vacancy

            Args:
                vac_dict (dict): данные об одной вакансии
            Returns:
                Vacancy: информация об одной вакансии в виде объекта Vacancy
        """
        salary = Salary(vac_dict['salary_from'], vac_dict['salary_to'],
                        vac_dict['salary_currency'])
        salary = salary.convert_to_rub()
        return Vacancy(vac_dict['name'], salary, vac_dict['area_name'],
                       int(vac_dict['published_at'][0:4]))

    def parse_csv(self):
        """Считывает данные из csv-файла и форматирует их"""

        rows, titles = reader.csv_reader(self.file_name)
        self.vacancies_objects = reader.csv_filer(rows, titles, self.create_vacancy)

class Vacancy:
    """Класс для представления вакансии

           Attributes:
               name (str): название профессии
               salary (Salary or float or int): зарплата
               area_name (str): место работы
               published_at (str or int): дата публикации
        """
    def __init__(self, name, salary, area, published_at):
        """Инициализирует объект Vacancy

            Args:
                name (str): название профессии
                salary (Salary or float or int): зарплата
                area (str): место работы
                published_at (str or int): дата публикации
        """
        self.name = name
        self.salary = salary
        self.area_name = area
        self.published_at = published_at

class Salary:
    """Класс для представления зарплаты

        Attributes:
            salary_from (str or int or float) : нижняя граница вилки оклада
            salary_to (str or int or float): верхняя граница вилки оклада
            salary_currency (str): валюта оклада
    """
    def __init__(self, salary_from, salary_to, currency):
        """Инициализирует объект Salary

            Args:
                salary_from (str or int or float) : нижняя граница вилки оклада
                salary_to (str or int or float): верхняя граница вилки оклада
                currency (str): валюта оклада
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
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
        >>> Salary(10,20,'USD').convert_to_rub()
        909.9
        >>> Salary(10.2,40.2,'RUR').convert_to_rub()
        25.0
        """
        average_salary = (float(self.salary_to) + float(self.salary_from)) // 2
        return average_salary * self.currency_to_rub[self.salary_currency]

class InputConnect:
    """Класс для формирования статистики по вакансиям

        Attributes:
            data_set (DataSet): набор данных по вакансиям
    """
    def __init__(self, data_set):
        """Инициализирует объект InputConnect

            Args:
                data_set (DataSet): набор данных по вакансиям
        """
        self.data_set = data_set

    def get_all_ages(self, list_objects):
        """Получает список неповторяющихся дат, в которые были опубликованы все вакансии

            Args:
                list_objects (list): список вакансий
            Returns:
                list: даты публикации вакансий
        """
        return list(set([vac.published_at for vac in list_objects]))

    def get_vacancies_by_age(self, age, list_objects):
        """Получает список вакансий, опубликованных в заданный год

           Args:
               age (str): год публикации
               list_objects (list): список вакансий
           Returns:
               list: отфильтрованный список вакансий, опубликованных в заданный год
        """
        return list(filter(lambda vac: vac.published_at == age, list_objects))

    def count_vacancies_by_ages(self, ages, all_objects, job_objects):
        """Считает количество вакансий, опубликованных за каждый год периода

           Args:
               ages (list): года публикации вакансий
               all_objects (list): список всех вакансий
               job_objects (list): список вакансий для выбранной профессии
            Returns:
                tuple: (статистика по годам для всех вакансий, статистика по годам для выбранной профессии)
        """
        statistics_job = {}
        statistics_all = {}
        for age in ages:
            statistics_job[age] = len(self.get_vacancies_by_age(age, job_objects))
            statistics_all[age] = len(self.get_vacancies_by_age(age, all_objects))
        return statistics_all, statistics_job

    def get_salary_by_age(self, age, list_objects):
        """Получает среднюю зарплату в заданный год

           Args:
               age (str): год публикации вакансии
               list_objects (list): список вакансий
            Returns:
                int: средняя зарплата в заданный год
        """
        vacancies = self.get_vacancies_by_age(age, list_objects)
        if len(vacancies) == 0:
            return 0
        sum_salaries = sum([float(vac.salary) for vac in vacancies])
        return int(sum_salaries // len(vacancies))

    def get_salary_by_ages(self, ages, all_objects, job_objects):
        """Получает статистику по уровню зарплат по годам

            Args:
                ages (list): список лет, когда были опубликованы вакансии
                all_objects (list): список всех вакансий
                job_objects (list): список вакансий для выбранной профессии
            Returns:
                tuple: (статистика по уровню зарплат по годам для всех вакансий,
                        статистика по уровню зарплат по годам для выбранной профессии)
        """
        statistics_job = {}
        statistics_all = {}
        for age in ages:
            statistics_job[age] = self.get_salary_by_age(age, job_objects)
            statistics_all[age] = self.get_salary_by_age(age, all_objects)
        return statistics_all, statistics_job

    def sort_cities_by_value(self, cities):
        """Сортирует данные статистики по городам по убыванию

            Args:
                cities (dict): словарь с городами и соответствующими статистическими значениями
            Returns:
                dict: данные статистики в убывающем порядке
        """
        return sorted(cities.items(), key=lambda item: item[1], reverse=True)

    def sort_cities(self, cities, cities_count):
        """Сортирует данные статистики и берет только первые cities_count значений

            Args:
                cities (dict): данные статистики по городам
                cities_count (int): количество элементов,до которого нужно обрезать данные после сортировки
            Returns:
                dict: первые 10 значений отсортированных данных статистики
        """
        sorted_list = self.sort_cities_by_value(cities)
        result = sorted_list[0:cities_count]
        cities = [item[0] for item in result]
        values = [item[1] for item in result]

        return dict(zip(cities, values))

    def count_vacancies_by_cities(self, vac_objects):
        """Считает количество вакансий по городам

           Args:
               vac_objects (list): список вакансий
            Returns:
                dict: количество вакансий в каждом из городов списка vac_objects
        """
        vac_cities = {}
        for vac in vac_objects:
            city = vac.area_name
            if city not in vac_cities.keys():
                vac_cities[city] = 1
            else:
                vac_cities[city] += 1
        return vac_cities

    def get_statistics_by_cities(self, vac_objects):
        """Получает статистику по городам

           Args:
               vac_objects (list): список вакансий
           Returns:
               tuple: (статистика по уровню зарплат в городах, доля вакансий по городам)
        """
        total_count = len(vac_objects)
        min_count = math.floor(total_count * 0.01)
        vac_cities = self.count_vacancies_by_cities(vac_objects)

        salary_level = {}
        vac_proportion = {city: round(n / total_count, 4) for city, n in vac_cities.items()
                          if n >= min_count}
        for city in vac_cities.items():
            if city[1] >= min_count:
                vacancies = list(filter(lambda vac: vac.area_name == city[0], vac_objects))
                if len(vacancies) == 0:
                    salary_level[city[0]] = 0
                else:
                    sum_salaries = sum([float(vac.salary) for vac in vacancies])
                    salary_level[city[0]] = int(sum_salaries // len(vacancies))

        salary_level = self.sort_cities(salary_level, 10)
        vac_proportion = self.sort_cities(vac_proportion, 10)
        return salary_level, vac_proportion

    def print_statistics(self, years, cities):
        """Печатает данные статистики

            Args:
                years (dict): статистика по годам
                cities (dict): статистика по городам
        """
        print(f"Динамика уровня зарплат по годам: {years['salary_all']}")
        print(f"Динамика количества вакансий по годам: {years['number_all']}")
        print(f"Динамика уровня зарплат по годам для выбранной профессии: {years['salary_job']}")
        print(f"Динамика количества вакансий по годам для выбранной профессии: {years['number_job']}")
        print(f"Уровень зарплат по городам (в порядке убывания): {cities['salary']}")
        print(f"Доля вакансий по городам (в порядке убывания): {cities['proportion']}")

    def get_statistics(self, vac_objects, job):
        """Получает статистические данные по вакансиям и для выбранной профессии

           Args:
               vac_objects (list): список вакансий
               job (str): название выбранной профессии
           Returns:
               tuple: (статистика по годам, статистика по городам)
        """
        job_objects = list(filter(lambda vac: job in vac.name, vac_objects))
        ages = self.get_all_ages(vac_objects)
        ages.sort()

        number_all, number_job = self.count_vacancies_by_ages(ages, vac_objects, job_objects)
        salary_all, salary_job = self.get_salary_by_ages(ages, vac_objects, job_objects)
        salary_cities, proportion_cities = self.get_statistics_by_cities(vac_objects)

        years_statistics = {'salary_all': salary_all,
                            'number_all': number_all,
                            'salary_job': salary_job,
                            'number_job': number_job}

        cities_statistics = {'salary': salary_cities,
                             'proportion': proportion_cities}

        self.print_statistics(years_statistics, cities_statistics)
        return years_statistics, cities_statistics
