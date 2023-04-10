"""
Задание №1
"""

some_list = ['разработка', 'сокет', 'декоратор']

for i in some_list:
    print(type(i))
    print(i)

print('----------------')

some_unic = ['\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
          '\u0441\u043e\u043a\u0435\u0442',
          '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440']

for i in some_unic:
    print(type(i))
    print(i)

# <class 'str'>
# разработка
# <class 'str'>
# сокет
# <class 'str'>
# декоратор
# ----------------
# <class 'str'>
# разработка
# <class 'str'>
# сокет
# <class 'str'>
# декоратор

print('==========================')

"""
Задание №2
"""

some_list = [b'class', b'function', b'method']
for i in some_list:
    print(type(i))
    print(i)
    print(len(i))

# <class 'bytes'>
# b'class'
# 5
# <class 'bytes'>
# b'function'
# 8
# <class 'bytes'>
# b'method'
# 6

print('==========================')

"""
Задание №3
"""

some_list = ['attribute', 'класс', 'функция', 'type']

for i in some_list:
    try:
        print(bytes(i, 'ascii'))
    except UnicodeEncodeError:
        print(f'"{i}" невозможно записать в байтовом типе')

# b'attribute'
# "класс" невозможно записать в байтовом типе
# "функция" невозможно записать в байтовом типе
# b'type'

print('==========================')

"""
Задание №4
"""


some_list = ['разработка', 'администрирование', '«protocol', 'standard']
for i in some_list:
    i_encode = i.encode('utf-8')
    i_decode = i_encode.decode('utf-8')

    print(i_encode)
    print(i_decode)
    print()
    
# b'\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0'
# разработка

# b'\xd0\xb0\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5'
# администрирование

# b'\xc2\xabprotocol'
# «protocol

# b'standard'
# standard

print('==========================')

"""
Задание №5
"""

import subprocess
import chardet


some_agrs = ['ping', 'yandex.ru']
ya_ping = subprocess.Popen(some_agrs, stdout=subprocess.PIPE)

for i in ya_ping.stdout:
    detect = chardet.detect(i)
    result = i.decode(detect['encoding']).encode('utf-8')
    print(result.decode('utf-8'))

# PING yandex.ru (77.88.55.60) 56(84) bytes of data.
# 64 bytes from yandex.ru (77.88.55.60): icmp_seq=1 ttl=245 time=13.7 ms
# 64 bytes from yandex.ru (77.88.55.60): icmp_seq=2 ttl=245 time=12.8 ms
# 64 bytes from yandex.ru (77.88.55.60): icmp_seq=3 ttl=245 time=12.8 ms


some_agrs = ['ping', 'youtube.com']
you_ping = subprocess.Popen(some_agrs, stdout=subprocess.PIPE)

for i in you_ping.stdout:
    detect = chardet.detect(i)
    result = i.decode(detect['encoding']).encode('utf-8')
    print(result.decode('utf-8'))

# PING youtube.com (64.233.164.91) 56(84) bytes of data.
# 64 bytes from lf-in-f91.1e100.net (64.233.164.91): icmp_seq=1 ttl=105 time=21.6 ms
# 64 bytes from lf-in-f91.1e100.net (64.233.164.91): icmp_seq=2 ttl=105 time=20.1 ms
# 64 bytes from lf-in-f91.1e100.net (64.233.164.91): icmp_seq=3 ttl=105 time=18.3 ms


"""
Задание №6
"""

from chardet.universaldetector import UniversalDetector


detect = UniversalDetector()

with open('Lesson_1/test_file.txt', 'rb') as f:
    for i in f:
        detect.feed(i)
        if detect.done:
            break
    detect.close()

print(detect.result['encoding'])


with open('Lesson_1/test_file.txt', encoding='utf-8') as f:
    for i in f.readlines():
        print(i)
        
f.close()

# utf-8
# сетевое программирование

# сокет

# декоратор
