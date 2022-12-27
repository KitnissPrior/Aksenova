import report as rep
import table as vac_table

if __name__ == '__main__':
    data_format = input()
    if data_format == 'Статистика':
        print('Введите данные для печати:')
        rep.get_report()
    if data_format == 'Вакансии':
        print('Введите данные для печати:')
        vac_table.get_vacancies_table()
