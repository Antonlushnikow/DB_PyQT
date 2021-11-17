"""2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только
последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение. """

import subprocess
import ipaddress
from sys import platform


HOSTS_START = '192.168.1.6'
HOSTS_END = '192.168.1.10'

is_windows = True if 'win' in platform else False
hops_arg = '-n' if is_windows else '-c'
shell_arg = True if is_windows else False


def host_ping(hosts):
    """Опрашивает адреса из списка hosts"""
    for h in hosts:
        try:
            h = ipaddress.ip_address(h)
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
                print(f'{h} - Узел доступен')
            else:
                print(f'{h} - Узел недоступен')
        except ValueError:
            print(f'Не удалось преобразить {h} в IP-адрес')


def host_range_ping(start, end):
    """Опрашивает адреса в диапазоне от start до end"""
    try:
        start = ipaddress.ip_address(start)
        end = ipaddress.ip_address(end)
        if end < start:
            print('Второй адрес должен быть больше первого')
            return
    except ValueError:
        print('Некорректный формат адресов')
    else:
        for ip_range in ipaddress.summarize_address_range(start, end):
            host_ping(ip_range)


if __name__ == "__main__":
    host_range_ping(HOSTS_START, HOSTS_END)
