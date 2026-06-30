import requests
from bs4 import BeautifulSoup
import re

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

class Model:

    def __init__(self):
        self.data = {}

    def get_brand(self, name: str) -> str:
        for key, value in brand_tag.items():
            if key in name:
                return value
        return "etc."

#
    def request_page(self, url: str) -> bool:
        try:
            res = requests.get(url)
            res.raise_for_status()
            self.data[url] = res.text
            return True
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return False

    def get_release_year(self, url: str) -> str:
        # おきちゃんのガンプラ堂
        res = re.match(r"https://kaigoshinootakunaburogu.com/gunpla-resale-calendar-(\d{4})", url)
        if res:
            return res.group(1)
        return "2026"

    def get_product_list(self, url: str, html: str):
        bs = BeautifulSoup(html, 'lxml')
        toc = bs.find('div', class_='toc')
        products = toc.find_all('a')
        product_list = {}
        year = self.get_release_year(url)
        date = year + "/01/01"

        date_compile = re.compile(r'(\d{1,2})月(\d{1,2})')
        canceled_compile = re.compile(r'.*【再販中止】になったガンプラ.*')
        postponed_date_compile = re.compile(r'(【.+月(追加再販|延期)分?】)')
        new_release = "【新作】"
        for product in products:
            if re.match(canceled_compile, product.text) is not None:
                break
            product_name = product.text
            # "【新作】"表記の削除
            if( product_name.find(new_release) == 0):
                product_name = product_name.replace(new_release,"")

            date_param = re.match(date_compile, product_name)
            if date_param is not None:
                # 日付なら出荷日を更新
                date = "{:04s}/{:02d}/{:02d}".format(year,int(date_param.group(1)), int(date_param.group(2)))
                product_list[date] = [] 
            else:
                # 延期や追加の表記削除
                match = re.search(postponed_date_compile, product_name)
                if match is not None:
                    product_name = product_name.replace(match.group(1),"")
                    brand_name = self.get_brand(product_name)                
                    product_array = product_list[date]
                    product_array.append({ product_name, brand_name })
                    product_list[date] = product_array
        return product_list

