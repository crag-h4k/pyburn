#!/usr/bin/env python3

from pprint import pprint
from multiprocessing import Pool, cpu_count
from psutil import sensors_temperatures
from datetime import datetime, timedelta
from sys import argv
from time import sleep

from colorama import Fore, Style


Fahrenheit = lambda C: C*(9/5) + 32


def heat_metrics( mins:int, cool:bool=True, device='nct6796', limit=0) -> None: # -> dict: # func=sq

    ts_0 = datetime.now()
    ts_d = timedelta(minutes=0)
    T0 = sensors_temperatures().get(device)[2].current
    T1 = sensors_temperatures().get(device)[2].current
    deg = '°'
    nc = Style.RESET_ALL

    if not cool:
        c = Fore.RED
        duration= timedelta(minutes=mins)
        limit = duration
        cond = ts_d >= limit

    else:
        c = Fore.BLUE
        cond = T1 <= limit

    while not cond:
        T1 = sensors_temperatures().get(device)[2].current
        ts_1 = datetime.now()
        ts_d = ts_1 - ts_0

        Td = T1 - T0
        ts_sec = ts_d.total_seconds()
        v = Td/ts_sec
        a = v/ts_sec

        str_Td = str(round(Td, 4))[:6]
        str_v = str(round(v, 4))[:6]
        str_a = str(round(a, 4))[:6]
        str_ts_d = str(ts_d)[:10]


        if not cool:
            cond = ts_d >= duration
        else:
            sleep(.15)
            cond = T1 <= limit

        output = ' {c}{}°{nc}  ΔT: {c}{}°{nc}  dT/dt:{c}{}°²  dv/dt:{c}{}°³  {nc}{}'.format(T1, str_Td, str_v, str_a, str_ts_d, c=c, nc=nc)
        print(output, end='\r')
    return


def burn(x: int=cpu_count()) -> heat_metrics:
    if x >= cpu_count():
        x = x - 1
    x * x

    return heat_metrics( mins = int(argv[2]), cool=False)


if __name__ == '__main__':

    parser = ArgumentParser(description='Track CPU heat and cooling')
    parser.add_argument('cpus',
            metavar='n_cpu',
            type=int,
            help='how many cpus to burn')
    parser.add_argument('time',
            metavar='limt',
            type=int,
            help='how long to burn in minutes')

    n_cpu = int(argv[1])
    ts = datetime.now()
    T0 = sensors_temperatures().get('nct6796')[2].current
    c =  Fore.GREEN
    nc = Style.RESET_ALL
    print(ts)
    print(' {c}{}°{nc} CPUs: {c}{}{nc}'.format(T0, n_cpu, c=c, nc=nc))
    with Pool(n_cpu) as p:
        p.map(burn, range(n_cpu))

    #print('\n End: {} at {c}{}°{nc}'.format(ts, T1, c=c, nc=nc))
    print(' Starting {}Cooling{nc} until {c}{}{nc}'.format(Fore.BLUE, T0, c=c, nc=nc))
    heat_metrics( mins = 1, cool=True, limit=T0)
