'''
Только для windows!!!
'''

import subprocess

process = []

while True:
    action = input('Выберите действие: q - выход , s - запустить сервер, '
                   'k - запустить клиенты x - закрыть все окна:')
    if action == 'q':
        break
    elif action == 's':
        process.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'k':
        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        for i in range(clients_count):
            process.append(subprocess.Popen(f'python client.py -n test{i + 1}', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'x':
        while process:
            process.pop().kill()


''' 
Только для Linux!!!
'''

# import time
# from subprocess import Popen


# process = []

        
# while True:
#     action = input('Команды:\n"s" - запустить сервер и клиентов\n"x" - закрыть все окна\n'
#                    '"q" - выйти\nВыберите действие: ')
#     if action == "q":
#         break
#     elif action == "s":
#         process.append(Popen('gnome-terminal -- python3 server.py', shell=True))
#         time.sleep(0.4)
#         process.append(Popen('gnome-terminal -- python3 client.py -n test_1', shell=True))
#         process.append(Popen('gnome-terminal -- python3 client.py -n test_2', shell=True))
#         process.append(Popen('gnome-terminal -- python3 client.py -n test_3', shell=True))      
#     elif action == "x":
#         while process:
#             victim = process.pop()
#             victim.kill()
#             victim.terminate()