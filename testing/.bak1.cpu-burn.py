#!/usr/bin/env python3

from pprint import pprint
from multiprocessing import Pool, Manager, Process, cpu_count
from psutil import sensors_temperatures
from datetime import datetime, timedelta
from sys import argv
from time import sleep

from colorama import Fore, Style


sq = lambda x: x**x
Fahrenheit = lambda C: (C * 9/5) + 32


def heat_metrics( mins:int, func=sq, burn:bool=True, x:int=cpu_count(), units='C', device='nct6796', ): # -> dict

    if x == cpu_count():
        x = x - 1

    ts_0 = datetime.now()
    ts_d = timedelta(minutes=0)
    T0 = sensors_temperatures().get(device)[2].current
    T1 = sensors_temperatures().get(device)[2].current

    no_clr = Style.RESET_ALL

    if burn:
        clr = Fore.RED
        duration= timedelta(minutes=mins)
        limit = duration
        cond = ts_d <= limit

    else:
        clr = Fore.BLUE
        cond = T0 >= T0 - .1

    print('Start: {} at {}{}°{}{}'.format(ts_0, clr, T0, units, no_clr))
    while cond:
        try:
            T1 = sensors_temperatures().get(device)[2].current
            ts_1 = datetime.now()
            ts_d = ts_1 - ts_0

            if units is 'F':
                T0 = Fahrenheit(T0)
                T1 = Fahrenheit(T1)

            Td = T1 - T0
            ts_sec = ts_d.total_seconds()
            v = Td/ts_sec
            a = v/ts_sec

            str_Td = str(round(Td, 3))
            str_v = str(round(v, 3))
            str_a = str(round(a, 3))
            str_ts_d = str(ts_d)[:-4]

            data = {'T0': T0,
                    'T1': T1,
                    'velocity':v,
                    'acceleration':a,
                    'run_time': ts_d,
                    }

            if burn:
                func(x)
                cond = ts_d <= duration
                str_cond = '<= {} burn'.format(duration)
            else:
                sleep(.1)
                cond = T0 <= T1
                str_cond = '{} <= {} no burn'.format(T0,T1)
            print('T: {}{}°{u}{}  ΔT: {}{}°{u}{}  dT/dt:{}°{u}²  dv/dt:{}°{u}³  {} {}'.format(clr, T1, no_clr, clr, str_Td, no_clr, str_v, str_a, str_ts_d, str_cond, u=units), end='\r')

        except KeyboardInterrupt:
            break;
    print('\nEnd: {} at {}{}°{}'.format(ts_1, clr, T1, no_clr))

    return data


if __name__ == '__main__':


    #n_cpu = int(argv[1])
    n_cpu = 4
    man = Manager()
    r_dict = man.dict()
    jobs = []
    t = heat_metrics( mins = .5, burn=True, x=n_cpu, units='C')
    for i in range(n_cpu):
        p = Process(target = t)
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()
device='nct6796'
    pprint(r_dict)
    heat_metrics( mins = 1, burn=False, x=0, units='C')
