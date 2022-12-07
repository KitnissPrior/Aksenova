import report as rep
import table as vac_table

data_format = input()
if data_format == 'Статистика':
    print('Введите данные для печати:')
    rep.get_report()
if data_format == 'Вакансии':
    print('Введите данные для печати:')
    vac_table.get_vacancies_table()

<<<<<<< HEAD
a = 1
=======
a = 2
>>>>>>> caa10886208c4dd4e425bae931e59d6d363924cd
