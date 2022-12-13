from unittest import TestCase
from datetime import datetime as module_dt
from table import Vacancy, Salary, DataSet, InputConnect

class TableVacanciesTest(TestCase):
    salary = Salary(100,200,'True','RUR')
    vacancy_programmer = Vacancy('Программист','Настоящий мегамозг','Усидчивость','moreThan6',
                      'True','Скб Контур',salary,'Екб','2022-05-31T17:32:31+0300')
    vacancy_designer = Vacancy('Дизайнер', 'Креативщик', ['Усидчивость, знание Photoshop'], 'moreThan6',
                                 'True', 'Скб Контур', salary, 'Екб', '2022-05-31T17:32:31+0300')
    vacancy_analyst = Vacancy('Аналитик', 'Будет работать с данными', 'Усидчивость', 'Более 6 лет',
                      'True', 'Скб Контур', salary, 'Екб', '2022-05-31T17:32:31+0300')
    dataset = DataSet('vacancies_table.csv')
    connector = InputConnect(dataset)
    def test_sort_by_date(self):
        self.assertEqual(self.connector.sort_by_date(self.vacancy_programmer),
                         module_dt(2022, 5, 31, 20, 32, 31))
    def test_sort_by_one_skill(self):
        self.assertEqual(self.connector.sort_by_skills(self.vacancy_programmer), 1)
    def test_sort_by_two_skills(self):
        self.assertEqual(self.connector.sort_by_skills(self.vacancy_designer),
                         len(self.vacancy_designer.key_skills))
    def test_sort_by_experience(self):
        self.assertEqual(self.connector.sort_by_experience(self.vacancy_programmer),3)
    def test_modify_number(self):
        self.assertEqual(self.connector.modify_number('10000'),'10 000')
    def test_formatter_salary(self):
        self.connector.formatter(self.vacancy_analyst)
        self.assertEqual(self.vacancy_analyst.salary,'100 - 200 (Рубли) (Без вычета налогов)')
    def test_check_input_values_empty(self):
        self.assertEqual(self.connector.check_input_values('','',''),'')





