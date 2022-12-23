import multiprocessing
import cProfile

def get_statistics_by_year(year, q):
    q.put ({'salary_all': 1000,
            'number_all': year,
            'salary_job': 1000 + int(year),
            'number_job': int(year)+30, })

def run_multoprocessing():
    years = [str(year) for year in range(2007, 2023)]
    stats_dict = {}
    ctx = multiprocessing.get_context('spawn')
    procs = []
    q = ctx.Queue()
    for year in years:
        p = ctx.Process(target=get_statistics_by_year, args=(year,q))
        p.start()
        procs.append(p)
        p.join()
        stats_dict[year] = q.get()
    print(stats_dict)

'''if __name__ =='__main__':
    cProfile.run('run_multoprocessing()')'''
from multiprocessing import Pool

def  f(x):
    return {'salary_all': 1000,
            'number_all': x,
            'salary_job': 1000 + int(x),
            'number_job': int(x)+30, }

def run():
    pool = Pool(processes=4)
    years = range(2007, 2022)
    result = pool.map(f, years)
    dict_res = {v['number_all']: v for v in result}
    print(result[0])

def run2():
    pool = Pool()
    res = pool.map_async(f, range(2007,2023)).get()
    dict_res = {v['number_all']: v for v in res}
    print(res)

if __name__ == '__main__':
    cProfile.run('run2()')