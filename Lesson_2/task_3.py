import yaml


some_dict = {'key_1': ['printer', 'scanner'],
             'key_2': 1,
             'key_3': {'printer': '10000₽', 'scanner': '100€'}}


with open('Lesson_2/file.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(some_dict, f, default_flow_style=False, allow_unicode=True)

with open('Lesson_2/file.yaml', 'r', encoding='utf-8') as f:
    data_dict = yaml.load(f, Loader=yaml.SafeLoader)
    print(some_dict == data_dict) # True

