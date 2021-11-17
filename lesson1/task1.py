"""1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или
ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции
ip_address(). """

import subprocess
import ipaddress
from sys import platform


MY_HOSTS = [
    '192.168.1.1',
    '192.168.1.2',
    '192.168.1.3',
    '192.168.1.4',
    '192.168.1.5',
    '8.8.8.8'
]

is_windows = True if 'win' in platform else False  # True, если Windows
hops_arg = '-n' if is_windows else '-c'  # флаг для числа скачков в зависимости от ОС
shell_arg = True if is_windows else False  # Значение аргумента shell


def host_ping(hosts):
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
                resp = True if 'мс' in out else False
            else:
                resp = True if not ret else False

            if resp:
                print(f'{h} - Узел доступен')
            else:
                print(f'{h} - Узел недоступен')
        except ValueError:
            print(f'Не удалось преобразить {h} в IP-адрес')


if __name__ == "__main__":
    host_ping(MY_HOSTS)
