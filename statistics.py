import math
import csv_reader as reader
import csv_parts_creator as files_creator
from multiprocessing import Pool
from currency import Currency
class DataSet:
    """Класс для представления набора данных статистики по вакансиям

        Attributes:
            folder_name (str): имя папки, содержащей файлы с данными по годам
            job (str): название профессии, по которой нужно получить статистику
            file_name (str): имя файла, из которого считываются данные
            vacancies_objects (list): список вакансий
            connector (InputConnect): объект, отвечающий за формирование данных статистики
    """
    def __init__(self, folder_name, job):
        """Инициализирует объект DataSet

           Args:
                folder_name (str): имя папки, содержащей файлы с данными по годам
                job (str): название профессии, по которой нужно получить статистику
        """
        self.folder_name = folder_name
        self.file_name = 'csv/vacancies_dif_currencies.csv'
        self.vacancies_objects = []
        self.connector = InputConnect(self,job)

    def create_vacancy(self, vac_dict, currency_dict):
        """Создает объект Vacancy

            Args:
                vac_dict (dict): данные об одной вакансии
            Returns:
                Vacancy: информация об одной вакансии в виде объекта Vacancy
        """
        salary = Salary(vac_dict['salary_from'], vac_dict['salary_to'],
                        vac_dict['salary_currency'], vac_dict['published_at'])
        salary = salary.convert_to_rub(currency_dict)

        return Vacancy(vac_dict['name'], salary, vac_dict['area_name'],
                       int(vac_dict['published_at'][0:4]))
    def parse_csv(self):
        """Считывает данные из csv-файла и разбивает их на отдельные файлы по годам"""
        data = reader.csv_reader(self.file_name)
        all_rows = data['all_rows']
        titles = data['titles']

        currency = Currency(all_rows, titles.index('salary_currency'))
        rows = currency.process_currencies(titles.index('published_at'))

        #files_creator.parse_by_years(all_rows,titles)
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
    def __init__(self, salary_from, salary_to, currency, published_at):
        """Инициализирует объект Salary

            Args:
                salary_from (str or int or float) : нижняя граница вилки оклада
                salary_to (str or int or float): верхняя граница вилки оклада
                currency (str): валюта оклада
        """
        if salary_from == '':
            salary_from = salary_to
        if salary_to == '':
            salary_to = salary_from
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_currency = currency
        self.published_at = published_at[0:7]

    def convert_to_rub(self, currency_dict):
        """Вычисляет среднюю зарплату из вилки и переводит в рубли при помощи
        словаря currency_to_rub

            Returns:
                float: средняя зарплата в рублях
        >>> salary = Salary(10,20,'USD','2003-01')
        >>> salary.convert_to_rub(Currency.get_currency_data())
        477.02250000000004
        >>> salary = Salary('','','RUR','2003-01')
        >>> salary.convert_to_rub(Currency.get_currency_data())
        ''
        >>> salary = Salary('',40.2,'RUR','2003-01')
        >>> salary.convert_to_rub(Currency.get_currency_data())
        40.2
        >>> salary = Salary(10.3,40.2,'РУБ','2003-01')
        >>> salary.convert_to_rub(Currency.get_currency_data())
        ''
        """
        if self.salary_from == '' and self.salary_to == '':
            return ''
        average_salary = (float(self.salary_to) + float(self.salary_from)) / 2
        if self.salary_currency == 'RUR':
            return average_salary
        if self.salary_currency not in currency_dict[self.published_at].keys():
            return ''
        currency = currency_dict[self.published_at][self.salary_currency]
        if currency == ' ':
            return ''
        return average_salary * float(currency)
class InputConnect:
    """Класс для формирования статистики по вакансиям

        Attributes:
            data_set (DataSet): набор данных по вакансиям
            job (str): название профессии, по которой нужно получить статистик
    """
    def __init__(self, data_set, job):
        """Инициализирует объект InputConnect

            Args:
                data_set (DataSet): набор данных по вакансиям
                job (str): название профессии, по которой нужно получить статистик
        """
        self.data_set = data_set
        self.job = job

    '''def get_salary_by_age(self, vacancies):
        """Получает среднюю зарплату в заданный год

           Args:
               vacancies (list): список вакансий
            Returns:
                int: средняя зарплата в заданный год
        """
        if len(vacancies) == 0:
            return 0
        sum_salaries = sum([float(vac.salary) for vac in vacancies])
        return int(sum_salaries // len(vacancies))

    def join_statistics_by_years(self, data_dict):
        """Объединяет данные статистики по годам

            Args:
                data_dict (dict) : словарь с данными статистики
            Returns:
                dict: уровень зарплат по годам для всех вакансий и для выбранной профессии,
                количество вакансий по годам для всех вакансий и для выбранной профессии
        """
        sorted(data_dict.items())
        salary_all = {}
        number_all = {}
        salary_job = {}
        number_job = {}
        for item in data_dict.items():
            salary_all[item[0]] = item[1]['salary_all']
            number_all[item[0]] = item[1]['number_all']
            salary_job[item[0]] = item[1]['salary_job']
            number_job [item[0]] = item[1]['number_job']

        return {'salary_all': salary_all,
                'number_all': number_all,
                'salary_job': salary_job,
                'number_job': number_job}

    def get_statistics_by_year(self, year):
        """Получает количество вакансий и уровень зарплат для всех вакансий
        и для выбранной профессии за один год
            Args:
                year (string) : год
            Returns:
                dict: количество вакансий и уровень зарплат для всех вакансий
        и для выбранной профессии за один год
        """
        file_path = f"{self.data_set.folder_name}/{year}.csv"
        rows, titles = reader.csv_reader(file_path)
        vac_list = reader.csv_filer(rows, titles, self.data_set.create_vacancy)
        job_list = list(filter(lambda vac: self.job in vac.name, vac_list))
        return {'year': year,
                'salary_all': self.get_salary_by_age(vac_list),
                'number_all': len(vac_list),
                'salary_job': self.get_salary_by_age(job_list),
                'number_job': len(job_list), }

    def run_multiprocessing(self):
        """Запускает обработку данных по годам, используя параллельные процессы"""
        years = [str(year) for year in range(2003, 2023)]

        pool = Pool(processes=1)
        stats_list = pool.map(self.get_statistics_by_year, years)
        res = {v['year']: v for v in stats_list}
        return self.join_statistics_by_years(res)'''

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

    def get_statistics(self):
        """Получает статистические данные по вакансиям и для выбранной профессии

            Returns:
                tuple: (статистика по годам, статистика по городам)
        """
        vac_objects = self.data_set.vacancies_objects
        job_objects = list(filter(lambda vac: self.job in vac.name, vac_objects))
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

