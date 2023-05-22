import csv
import re
import chardet


def get_data(file_obj):
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = []

    for file in file_obj:
        with open(file, 'br') as f:
            bytes_data = f.read()
            data = decode_to_utf8(bytes_data)

            os_prod_el = re.split('Изготовитель системы:\s*', data)[1].split('\r')[0]
            os_name_el = re.split('Название ОС:\s*', data)[1].split('\r')[0]
            os_code_el = re.split('Код продукта:\s*', data)[1].split('\r')[0]
            os_type_el = re.split('Тип системы:\s*', data)[1].split('\r')[0]

            os_prod_list.append(os_prod_el)
            os_name_list.append(os_name_el)
            os_code_list.append(os_code_el)
            os_type_list.append(os_type_el)

    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(headers)
    for i in range(len(os_prod_list)):
        main_data.append([os_prod_list[i].strip(), os_name_list[i].strip(),
                          os_code_list[i].strip(), os_type_list[i].strip()])

    return main_data


def decode_to_utf8(bytes_string: bytes) -> str:
    result_encoding = chardet.detect(bytes_string)['encoding']
    decode_string = bytes_string.decode(result_encoding)
    string_utf8 = decode_string.encode('utf-8')
    return string_utf8.decode('utf-8')

def write_to_csv(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        result = csv.writer(f)
        result.writerows(data)


if __name__ == '__main__':
    lst = ['Lesson_2/info_1.txt', 'Lesson_2/info_2.txt', 'Lesson_2/info_3.txt']
    data = get_data(lst)

    write_to_csv('Lesson_2/report.csv', data)
