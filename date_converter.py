import maya
import arrow
import datetime
from datetime import datetime as module_dt
from dateutil.parser import parse as dt_parser
import cProfile

def profile(func):
    """Профилизатор
       Args:
           func (function): функция, время выполнения которой нужно измерить
        Returns:
            function: функция, измеряющая время работы функции func
    """
    def wrapper(*args, **kwargs):
        profile_filename = func.__name__ + '.prof'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result

    return wrapper

def convert_to_date(str_date):
    """Преобразует дату и время из строки в формат даты-времени с помощью
    утилиты dateutil.parser

    Args:
        str_date (str): дата и время
    Returns:
         datetime.datetime: дата и время с учетом часового пояса
    """
    date = dt_parser(str_date, ignoretz=True)

    parts = str_date.split('T')
    time = parts[1]
    operation = time[8]
    delta = datetime.timedelta(hours=int(time[9:11]), minutes=int(time[11::]))

    return date + delta if operation == '+' else date - delta


'''
def make_date_format_strptime(self, str_date):
    parts = str_date.split('T')
    time = parts[1]
    operation = time[8]

    delta = datetime.timedelta(hours=int(time[9:11]), minutes=int(time[11::]))
    date = module_dt.strptime(f"{parts[0]} {time[0:8]}", "%Y-%m-%d %H:%M:%S")

    return date + delta if operation == '+' else date - delta

def make_date_format_arrow(self, str_date):
    date = arrow.get(str_date)
    parts = str_date.split('T')
    time = parts[1]
    operation = time[8]
    delta = datetime.timedelta(hours=int(time[9:11]), minutes=int(time[11::]))

    return date + delta if operation == '+' else date - delta

def make_date_format_maya(self, str_date):
    date = maya.parse(str_date).datetime()

    parts = str_date.split('T')
    time = parts[1]
    operation = time[8]
    delta = datetime.timedelta(hours=int(time[9:11]), minutes=int(time[11::]))

    return date + delta if operation == '+' else date - delta
'''