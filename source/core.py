from bs4 import BeautifulSoup
import tkinter
import re
import requests

brand_tag= {
    "Figure-rise Standard Amplified" : "FrS Amplified",
    "Figure-rise Standard": "FrS",
    "MGSD": "MGSD",
    "HG": "HG",
    "MG": "MG",
    "RG": "RG",
    "PG": "PG",
    "SD": "SD",
    "ENTRY GRADE" : "EG",
    "EG" : "EG",
    "RE/100": "RE/100",
    "30 MINUTES MISSONS" : "30MM",
    "30MM" : "30MM",
    "30 MINUTES SISTERS" : "30MS",
    "30MS" : "30MS",
    "30 MINUTES FANTASY" : "30MF",
    "30MF" : "30MF",
    "30 MINUTES PREFARENS" : "30MP",
    "30MP" : "30MP",
 }

class Product:
    def __init__(self, name: str, release_date: str):
        self.name = name
        self.release_date = release_date
        self.brand = self.get_brand(name)

    def get_brand(self, name: str) -> str:
        for key, value in brand_tag.items():
            if key in name:
                return value
        return "etc."

def get_release_date(model_name: str) -> str:
    """Return a placeholder release date for the given model name."""
    return "1970-01-01"

def scraping(name : str):
    print(get_release_date(name))

    url = 'https://kaigoshinootakunaburogu.com/gunpla-resale-calendar-2026july'
    res = requests.get(url)
    print(res.status_code)
    print(res.headers['date'])

    bs = BeautifulSoup(res.text,'lxml')
    toc = bs.find('div', class_='toc')
    products= toc.find_all('a')

    date = '00/00'
    date_compile = re.compile(r'(\d{1,2})月(\d{1,2})')
    canceled_compile = re.compile(r'.*【再販中止】になったガンプラ.*')
    postponed_date_compile = re.compile(r'(【.+月(追加再販|延期)分?】)')
    new_release = "【新作】"
    for product in products:
        if re.match(canceled_compile, product.text) is not None:
            break
        product_name = product.text
        if( product_name.find(new_release) == 0):
            product_name = product_name.replace(new_release,"")
        date_param = re.match(date_compile, product_name)
        if date_param is not None:
            date = "{:02d}/{:02d}".format(int(date_param.group(1)), int(date_param.group(2)))
            print(date)
        else:
            match = re.search(postponed_date_compile, product_name)
            if match is not None:
                product_name = product_name.replace(match.group(1),"")
            print(product_name)
