from unittest import TestCase
import csv_reader as reader
import statistics as stats

class CsvTests(TestCase):
    def test_clear_str(self):
        self.assertEqual(reader.clear_str('<p>text</p>'),'text')
    def test_clear_empty_str(self):
        self.assertEqual(reader.clear_str(''),'')
    def test_clear_str_without_tags(self):
        self.assertEqual(reader.clear_str('text'),'text')

    rows = [['IT аналитик', '35000.0', '45000.0', 'RUR', 'Санкт-Петербург', '2007-12-03T17:34:36+0300']]
    titles = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
    data_set = stats.DataSet("vacancies.csv")
    def test_reader_one_row_in_file(self):
        self.assertEqual(reader.csv_reader("vacancies_one_row.csv"),(self.rows,self.titles))
    def test_reader_empty_file(self):
        self.assertEqual(reader.csv_reader("vacancies_empty.csv"),([],[]))
    def test_csv_filter_empty_data(self):
        self.assertEqual(len(reader.csv_filer([], [], self.data_set.create_vacancy)), 0)
    def test_csv_filter_one_vacancy(self):
        self.assertEqual(len(reader.csv_filer(self.rows,self.titles, self.data_set.create_vacancy)), 1)
    def test_csv_filter_vacancy_name(self):
        self.assertEqual((reader.csv_filer(self.rows,self.titles, self.data_set.create_vacancy))[0].name,
                         'IT аналитик')



