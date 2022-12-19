import csv

def create_csv_files(data_dict, titles):
    """Создает csv-файлы с данными по годам

    Args:
        data_dict (dict): данные о вакансиях, разделенные по годам
        titles (list): заголовки столбцов
    """
    for item in data_dict.items():
        title = item[0]
        with open(f"years_data/{title}", 'w', encoding='utf-8-sig') as f:
            writer = csv.writer(f,lineterminator="\r")
            writer.writerow(titles)
            writer.writerows(item[1])

def parse_by_years(rows,titles):
    """Разбивает данные о вакансиях по годам публикации,
    создавая для каждого года отдельный csv-файл

        Args:
            rows (list): строки, считанные из общей выгрузки
            titles (list): заголовки столбцов
    """
    years_dict = {}
    date_index = titles.index('published_at')
    for row in rows:
        year = f"{row[date_index][0:4]}.csv"
        if year not in years_dict.keys():
            years_dict[year] = []
        years_dict[year].append(row)
    create_csv_files(years_dict,titles)
