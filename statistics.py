import re
import csv
import math

class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies_objects = []
        self.connector = InputConnect(self)

    def csv_reader(self):
        with open(self.file_name, 'r', encoding='utf-8-sig') as file:
            data = list(csv.reader(file))

            titles = data[0]
            rows = [row for row in data[1:] if '' not in row and len(row) == len(titles)]
            return rows, titles

    def clear_str(self, str_value):
        return ' '.join(re.sub(r"\<[^>]*\>", '', str_value).split())

    def create_vacancy(self, vac_dict):
        salary = Salary(vac_dict['salary_from'], vac_dict['salary_to'],
                        vac_dict['salary_currency'])
        salary = salary.convert_to_rub()
        return Vacancy(vac_dict['name'], salary, vac_dict['area_name'],
                       int(vac_dict['published_at'][0:4]))

    def csv_filer(self, rows, titles):
        result = []
        for i in range(len(rows)):
            row = rows[i]
            for j in range(len(row)):
                row[j] = self.clear_str(row[j])

            vac_dict = dict(zip(titles, row))
            result.append(self.create_vacancy(vac_dict))
        return result

    def parse_csv(self):
        rows, titles = self.csv_reader()
        self.vacancies_objects = self.csv_filer(rows, titles)

class Vacancy:
    def __init__(self, name, salary, area, published_at):
        self.name = name
        self.salary = salary
        self.area_name = area
        self.published_at = published_at

class Salary:
    def __init__(self, salary_from, salary_to, currency):
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
        average_salary = (float(self.salary_to) + float(self.salary_from)) // 2
        return average_salary * self.currency_to_rub[self.salary_currency]

class InputConnect:
    def __init__(self, data_set):
        self.data_set = data_set

    def get_all_ages(self, list_objects):
        return list(set([vac.published_at for vac in list_objects]))

    def get_vacancies_by_age(self, age, list_objects):
        return list(filter(lambda vac: vac.published_at == age, list_objects))

    def count_vacancies_by_ages(self, ages, all_objects, job_objects):
        statistics_job = {}
        statistics_all = {}
        for age in ages:
            statistics_job[age] = len(self.get_vacancies_by_age(age, job_objects))
            statistics_all[age] = len(self.get_vacancies_by_age(age, all_objects))
        return statistics_all, statistics_job

    def get_salary_by_age(self, age, list_objects):
        vacancies = self.get_vacancies_by_age(age, list_objects)
        if len(vacancies) == 0:
            return 0
        sum_salaries = sum([float(vac.salary) for vac in vacancies])
        return int(sum_salaries // len(vacancies))

    def get_salary_by_ages(self, ages, all_objects, job_objects):
        statistics_job = {}
        statistics_all = {}
        for age in ages:
            statistics_job[age] = self.get_salary_by_age(age, job_objects)
            statistics_all[age] = self.get_salary_by_age(age, all_objects)
        return statistics_all, statistics_job

    def sort_cities_by_name(self, cities):
        return sorted(cities.items(), key=lambda item: item[1], reverse=True)

    def sort_cities(self, cities):
        sorted_list = self.sort_cities_by_name(cities)
        result = sorted_list[0:10]
        cities = [item[0] for item in result]
        values = [item[1] for item in result]

        return dict(zip(cities, values))

    def get_vacancies_by_cities(self, vac_objects):
        vac_cities = {}
        for vac in vac_objects:
            city = vac.area_name
            if city not in vac_cities.keys():
                vac_cities[city] = 1
            else:
                vac_cities[city] += 1
        return vac_cities

    def get_statistics_by_cities(self, vac_objects):
        total_count = len(vac_objects)
        min_count = math.floor(total_count * 0.01)
        vac_cities = self.get_vacancies_by_cities(vac_objects)

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

        salary_level = self.sort_cities(salary_level)
        vac_proportion = self.sort_cities(vac_proportion)
        return salary_level, vac_proportion

    def print_statistics(self, years, cities):
        print(f"Динамика уровня зарплат по годам: {years['salary_all']}")
        print(f"Динамика количества вакансий по годам: {years['number_all']}")
        print(f"Динамика уровня зарплат по годам для выбранной профессии: {years['salary_job']}")
        print(f"Динамика количества вакансий по годам для выбранной профессии: {years['number_job']}")
        print(f"Уровень зарплат по городам (в порядке убывания): {cities['salary']}")
        print(f"Доля вакансий по городам (в порядке убывания): {cities['proportion']}")

    def get_statistics(self, vac_objects, job):
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
