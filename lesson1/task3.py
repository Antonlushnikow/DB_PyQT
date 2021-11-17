"""3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
(использовать модуль tabulate)."""

import subprocess
import ipaddress
from sys import platform
from tabulate import tabulate

HOSTS_START = '192.168.1.1'
HOSTS_END = '192.168.1.5'


is_windows = True if 'win' in platform else False  # True, если Windows
hops_arg = '-n' if is_windows else '-c'  # флаг для числа скачков в зависимости от ОС
shell_arg = True if is_windows else False  # Значение аргумента shell


def host_range_ping_tab(start, end):
    """Опрашивает адреса в диапазоне от start до end"""

    print('Идет опрос IP-адресов...')

    try:
        start = ipaddress.ip_address(start)
        end = ipaddress.ip_address(end)
        if end < start:
            print('Второй адрес должен быть больше первого')
            return
    except ValueError:
        print('Некорректный формат адресов')
    else:
        reachable_list = []
        unreachable_list = []

        for ip_range in ipaddress.summarize_address_range(start, end):
            for h in ip_range:
                with subprocess.Popen(['ping', h.compressed, hops_arg, '2'], shell=shell_arg, stdout=subprocess.PIPE) as p:
                    p.wait()
                    out, _ = p.communicate()
                    out = out.decode('cp866')
                    ret = p.returncode

                if is_windows:
                    # Если ОС - Windows
                    resp = True if 'мс' in out or 'ms' in out else False
                else:
                    resp = True if not ret else False

                if resp:
                    reachable_list.append(h)
                else:
                    unreachable_list.append(h)

        print(tabulate({"Reachable": reachable_list, "Unreachable": unreachable_list}, headers="keys"))


if __name__ == "__main__":
    host_range_ping_tab(HOSTS_START, HOSTS_END)
