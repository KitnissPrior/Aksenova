import re
import csv
import os
from currency import Currency

def csv_reader(file_name):
    """Считывает данные из csv-файла

       Args:
           file_name (str): название csv-файла

       Returns:
           tuple: (считанные строки, заголовки строк)
    """
    with open(file_name, 'r', encoding='utf-8-sig') as file:
        data = list(csv.reader(file))

        titles = data[0] if (os.stat(file_name).st_size != 0) else []
        count = len(titles)

        all_rows = data[1:]
        rows = [row for row in all_rows if '' not in row and len(row) == count]
        return {'all_rows': all_rows,
                'rows': rows,
                'titles': titles}

def clear_str(str_value):
    """Очищает строку от html-тегов

       Args:
           str_value (str): входная строка
       Returns:
           str: строка без html-тегов
    """
    return ' '.join(re.sub(r"\<[^>]*\>", '', str_value).split())

def add_100_vacancies_to_csv(vacancies):
    """Добавляет первые 100 считанных вакансий в csv-файл

        Args:
            vacancies (list): строки с информацией о вакансиях
    """
    with open("100vacancies.csv", 'w', encoding='utf-8-sig') as f:
        writer = csv.writer(f, lineterminator="\r")
        writer.writerow(['name', 'salary', 'area_name','published_at'])
        writer.writerows(vacancies)

def csv_filer(rows, titles, create_vacancy):
    """Форматирует данные, считанные из csv-файла, формирует из них
    список объектов Vacancy и записывает первые 100 строк в csv-файл

        Args:
            rows (list): список строк, считанных из файла
            titles (list): названия строк, считанных из файла
            create_vacancy (function) : функция, создающая об]ект Vacancy
        Returns:
            list: список объектов Vacancy
    """
    result = []
    hundred_vacancies = []
    currency_dict = Currency.get_currency_data()
    for line_num in range(len(rows)):
        for i in range(len(rows[line_num])):
            field = rows[line_num][i]
            if field.find('\n') != -1:
                rows[line_num][i] = [clear_str(el) for el in field.split('\n')]
            else:
                rows[line_num][i] = clear_str(field)
        vac_dict = dict(zip(titles, rows[line_num]))
        vacancy = create_vacancy(vac_dict, currency_dict)
        if line_num < 100:
            hundred_vacancies.append([vacancy.name, vacancy.salary, vacancy.area_name, vac_dict['published_at']])
        if vacancy.salary != '':
            result.append(vacancy)
    add_100_vacancies_to_csv(hundred_vacancies)
    return result


