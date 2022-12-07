import statistics as stats
import report as rep

file_name = input('Введите название файла: ')
job = input('Введите название профессии: ')

data_set = stats.DataSet(file_name)
data_set.parse_csv()
years, cities = data_set.connector.get_statistics(data_set.vacancies_objects, job)

report = rep.Report(job)
report.generate_pdf(years, cities)
