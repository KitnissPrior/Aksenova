import re
import csv

def csv_reader(file_name):
    """Считывает данные из csv-файла

       Args:
           file_name (str): название csv-файла

       Returns:
           tuple: (считанные строки, заголовки строк)
    """
    with open(file_name, 'r', encoding='utf-8-sig') as file:
        data = list(csv.reader(file))

        titles = data[0]
        count = len(titles)
        rows = [row for row in data[1:] if '' not in row and len(row) == count]
        return rows, titles

def clear_str(str_value):
    """Очищает строку от html-тегов

       Args:
           str_value (str): входная строка
       Returns:
           str: строка без html-тегов
        """
    return ' '.join(re.sub(r"\<[^>]*\>", '', str_value).split())

def csv_filer(rows, titles, create_vacancy):
    """Форматирует данные, считанные из csv-файла и формирует из них
    список объектов Vacancy

        Args:
            rows (list): список строк, считанных из файла
            titles (list): названия строк, считанных из файла
        Returns:
            list: список объектов Vacancy
    """
    result = []
    for line in range(len(rows)):
        for i in range(len(rows[line])):
            field = rows[line][i]
            if field.find('\n') != -1:
                rows[line][i] = [clear_str(el) for el in field.split('\n')]
            else:
                rows[line][i] = clear_str(field)
        vacancy_dict = dict(zip(titles, rows[line]))
        result.append(create_vacancy(vacancy_dict))
    return result
