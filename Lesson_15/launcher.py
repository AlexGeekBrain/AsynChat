"""
Linux
"""
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

"""
Windows
"""
# import subprocess


# def main():
#     process = []

#     while True:
#         action = input(
#             'Выберите действие: q - выход , s - запустить сервер, k - запустить клиенты x - закрыть все окна:')
#         if action == 'q':
#             break
#         elif action == 's':
#             process.append(
#                 subprocess.Popen(
#                     'python server.py',
#                     creationflags=subprocess.CREATE_NEW_CONSOLE))
#         elif action == 'k':
#             print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123456.')
#             print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
#             clients_count = int(
#                 input('Введите количество тестовых клиентов для запуска: '))
#             # Запускаем клиентов:
#             for i in range(clients_count):
#                 process.append(
#                     subprocess.Popen(
#                         f'python client.py -n test{i + 1} -p 123456',
#                         creationflags=subprocess.CREATE_NEW_CONSOLE))
#         elif action == 'x':
#             while process:
#                 process.pop().kill()


# if __name__ == '__main__':
#     main()
