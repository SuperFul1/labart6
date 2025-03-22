import json
import matplotlib.pyplot as plt
import os
import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Union, Tuple

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Currencies(metaclass=Singleton):
    last_updated: int = 0  # Последнее обновление данных
    update_interval: int = 3600  # Интервал обновления в секундах

    @classmethod
    def get_currencies_json(cls, url: str = 'http://www.cbr.ru/scripts/XML_daily.asp', 
                            save_json: bool = False, 
                            file_name: str = 'currencies.json') -> Union[List[Dict[str, str]], str]:

        curr_time = time.time()

        if os.path.exists(file_name) and curr_time - os.path.getmtime(file_name) < cls.update_interval:
            with open(file_name, 'r', encoding='utf-8') as file:
                return json.load(file)

        response = requests.get(url)

        if response.status_code == 200:
            xml_data = response.content
            soup = BeautifulSoup(xml_data, 'lxml-xml')
            all_valutes = soup.find_all('Valute')

            currencies_list = []
            for valute in all_valutes:
                name = valute.find('Name').text.strip()
                code = valute.find('CharCode').text.strip()
                value = valute.find('Value').text.strip()
                nominal = valute.find('Nominal').text.strip()
                currencies_list.append({'name': name, 
                                        'code': code, 
                                        'value': value, 
                                        'nominal': nominal})

            cls.last_updated = curr_time

            if save_json:
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(currencies_list, file, ensure_ascii=False, indent=4)

            return currencies_list
        else:
            return 'Ошибка обработки данных'

    @classmethod
    def get_currency_value(cls, currency_identifier: str) -> Union[None, Tuple[str, str, str, str]]:

        currencies_list = cls.get_currencies_json()
        for valute in currencies_list:
            if valute['code'] == currency_identifier or valute['name'].lower() == currency_identifier.lower():
                return valute['name'], valute['code'], valute['value'], valute['nominal']
        return None

    @classmethod
    def visualize_currencies(cls, save_to_file: bool = False, file_name: str = 'currency_values.png') -> None:

        currencies_list = cls.get_currencies_json()
        names = [valute['name'] for valute in currencies_list]
        values = [float(valute['value'].replace(',', '.')) / int(valute['nominal']) for valute in currencies_list]

        plt.figure(figsize=(15, 8))
        bars = plt.bar(names, values, color='blue')
        plt.title('Currency Values')
        plt.xlabel('Currency')
        plt.ylabel('Value in RUB')
        plt.xticks(rotation=90)
        plt.tight_layout()  # корректирование графика для лучшего отображения

        if save_to_file:
            plt.savefig(file_name)

        plt.show()

currency_info = Currencies.get_currency_value('USD')  
if currency_info:
    name, code, value, nominal = currency_info
    print(f"Name: {name}, Code: {code}, Value: {value}, Nominal: {nominal}")
else:
    print("Currency not found")

all_currencies = Currencies.get_currencies_json(save_json=True)
for currency in all_currencies:
    print(currency)

Currencies.visualize_currencies(save_to_file=True)


c_1 = Currencies()

c_2 = Currencies()

print(id(c_1), id(c_2), sep='\n')
assert id(c_1) == id(c_2)
assert c_1 is c_2