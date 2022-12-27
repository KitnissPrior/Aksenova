from unittest import TestCase
from statistics import Vacancy, DataSet

class Statistics_Test(TestCase):
    dataset= DataSet("vacancies_diff_currencies.csv", "Программист")
    connector = dataset.connector
    vacancies = []
    vacancies.append(Vacancy('Программист', 1000, 'Екатеринбург', '2022'))
    vacancies.append(Vacancy('Аналитик', 1000, 'Екатеринбург', '2021'))
    vacancies.append(Vacancy('Дизайнер', 1200, 'Томск', '2022'))
    def test_sort_cities(self):
        cities = {'Москва':20, 'Екб':10, 'Омск': 0, 'Томск':14, 'Вологда': 30,
                  'Ярославль':34, 'Питер': 8, 'Березовский' :12, 'Серов': 17,
                  'Челябинск': 15, 'Нижний Тагил':5, 'Кострома': 9}
        self.assertEqual(self.connector.sort_cities(cities, 3),{'Ярославль':34,'Вологда': 30,'Москва':20,})
    def test_count_vacancies_by_cities(self):
        self.assertEqual(self.connector.count_vacancies_by_cities(self.vacancies), {'Екатеринбург': 2, 'Томск':1})
    def test_count_vacancies_by_cities_empty_list(self):
        self.assertEqual(self.connector.count_vacancies_by_cities([]), {})
    def test_get_salary_by_age(self):
        self.assertEqual(self.connector.get_salary_by_age(self.vacancies),1066)


