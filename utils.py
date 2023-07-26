import multiprocessing as mp
from concurrent import futures
from multiprocessing import cpu_count

def pygrep(file, grep):
    with open(file,'r') as a:
        ls=a.readlines()
        filtered=[]
        for l in ls:
            if grep in l:
                filtered.append(l)
        print(''.join(filtered))


def pycat(file):
    with open(file,'r') as a:
        ls=a.read()
        print(ls)


def parallel_runs(func, data_lists, proc=None):
    with futures.ProcessPoolExecutor(max_workers=proc) as executor:
        result_list = executor.map(func, *data_lists)
    return result_list


def parallel_runs_mp(func, data_lists, parallel_mode=1, proc=None):
    if not proc:
        proc = cpu_count()
    mp_modes = ['fork', 'spawn', 'forkserver']
    mp_mode = mp_modes[parallel_mode]
    try:
        mp.set_start_method(mp_mode, force=True)
        print(mp_mode + 'ed')
    except RuntimeError:
        print('set mp mode failed')
        pass
    pool = mp.Pool(proc)
    result_list = pool.starmap(func, data_lists)
    return result_list