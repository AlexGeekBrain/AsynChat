from subprocess import PIPE, Popen
from ipaddress import ip_address


def host_ping(ip_addr, n=2, w=1):
    options = {0: 'доступен', 1: 'не доступен'}
    result = {'доступен': [], 'не доступен': []}

    for addr in ip_addr:
        try:
            addr = ip_address(addr)
        except ValueError:
            pass

        proc = Popen(f'ping {addr} -n {n} -w {w}', shell=True, stdout=PIPE)
        proc.wait()
        result[options[proc.returncode]].append(str(addr))
        print(f'Узел {addr} - {options[proc.returncode]}')
    return result


if __name__ == '__main__':
    ip_list = ['192.168.0.100', '127.0.0.1', 'ya.ru', 'google.com']
    host_ping(ip_list)

"""
Узел 192.168.0.100 - не доступен
Узел 127.0.0.1 - не доступен
Узел ya.ru - доступен
Узел google.com - доступен
"""