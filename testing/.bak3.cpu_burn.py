#!/usr/bin/env python3

from pprint import pprint
from multiprocessing import Pool,cpu_count
from psutil import sensors_temperatures
from datetime import datetime, timedelta
from sys import argv
from time import sleep

from colorama import Fore, Style


sq = lambda x: x**x
Fahrenheit = lambda C: (C * 9/5) + 32


def burn(x: int=cpu_count()):
    if x >= cpu_count():
        x = x - 1
    x * x
    heat_metrics( mins = 1, cool=False, units='C')

def heat_metrics( mins:int, cool:bool=True, units='C', device='nct6796', limit=0): # -> dict func=sq

    ts_0 = datetime.now()
    ts_d = timedelta(minutes=0)
    T0 = sensors_temperatures().get(device)[2].current
    T1 = sensors_temperatures().get(device)[2].current

    no_clr = Style.RESET_ALL

    if not cool:
        clr = Fore.RED
        duration= timedelta(minutes=mins)
        limit = duration
        cond = ts_d <= limit

    else:
        clr = Fore.BLUE
        cond = T0 >= limit

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

            if not cool:
                cond = ts_d <= duration
            else:
                #sleep(.1)
                cond = T1 >= limit
            print('T: {}{}°{u}{}  ΔT: {}{}°{u}{}  dT/dt:{}°{u}²  dv/dt:{}°{u}³  {}'.format(clr, T1, no_clr, clr, str_Td, no_clr, str_v, str_a, str_ts_d, u=units), end='\r')

        except KeyboardInterrupt:
            break;
    print('\nEnd: {} at {}{}°{}'.format(str_ts_d, clr, T1, no_clr))

if __name__ == '__main__':
    #n_cpu = arvg[1]
    n_cpu = 8
    lim = sensors_temperatures().get('nct6796')[2].current
    with Pool(n_cpu) as p:
        p.map(burn, range(n_cpu))
    print('Starting {}Cooling{} until {}{}{}'.format(Fore.BLUE, Style.RESET_ALL, Fore.GREEN, lim, Style.RESET_ALL))
    heat_metrics( mins = 1, cool=True, units='C', limit=lim)
