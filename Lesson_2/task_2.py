import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('Lesson_2/orders.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open('Lesson_2/orders.json', 'w', encoding='utf-8') as f:
        order_list = data['orders']
        new_order = {'item': item, 'quantity': quantity, 'price': price,
                     'buyer': buyer, 'date': date}
        order_list.append(new_order)
        json.dump(data, f, indent=4, ensure_ascii=False)


write_order_to_json('printer', '1', '16000', 'Сидоров А.А,', '01.01.2023')
write_order_to_json('scanner', '2', '10000', 'Petrov P.P.', '02.02.2023')
write_order_to_json('монитор', '3', '20000', 'Иванов И.И.', '04.04.2023')
write_order_to_json('мышка', '4', '6000', 'Sobolev A.V.', '05.05.2023')
