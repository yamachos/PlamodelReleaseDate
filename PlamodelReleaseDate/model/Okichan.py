# python standard
import re
from datetime import date

# 3rdparty
from bs4 import BeautifulSoup
# 
from model.GoogleCalendar import GoogleCalendar
from model.ModelBase import ModelBase

class Model(ModelBase):
    MONTH_ENGLISH_STRINGS = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december"
    ]

    SCRAPING_PAGE_URL_BASE = "https://kaigoshinootakunaburogu.com/gunpla-resale-calendar-"

    BREAK_PRODUCT_LIST_STRINGS = [
        r'.*【再販中止】になったガンプラ.*',
        r'\d+年\d+月のガンプラ再販キット【注目ランキング】',
        r'\d+年ガンプラ再販スケジュールまとめ',
        r'ガンプラ再販アンケート'
    ]

    def __init__(self):
        super().__init__()
        self.calendar = GoogleCalendar()
        self.compiled_break_strs = []
        for break_str in self.BREAK_PRODUCT_LIST_STRINGS:
            self.compiled_break_strs.append( re.compile( break_str ) )

    # 指定したURLから年を取得する
    def get_release_date(self, url: str) -> str:
        # おきちゃんのガンプラ堂
        match_text = self.SCRAPING_PAGE_URL_BASE + r'(\d{4})' + r'{(' + '|'.join( self.MONTH_ENGLISH_STRINGS ) + r')}'
        res = re.match(match_text, url)
        if res:
            return date( int(res.group(1)), int(res.group(2)), 1)
        return self.DEFAULT_DATE

    # 指定した年と月からURLを生成する
    def get_url( self, year: int, month: int ) -> str:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        month_name = self.MONTH_ENGLISH_STRINGS[month - 1]
        return f"{self.SCRAPING_PAGE_URL_BASE}{str(year)}{month_name}"

    # 製品リストを取得する
    def get_product_list(self, url: str, html: str):
        bs = BeautifulSoup(html, 'lxml')
        toc = bs.find('div', class_='toc')
        products = toc.find_all('a')
        product_list = {}
        self.date = self.get_release_date(url)

        date_compile = re.compile(r'(\d{1,2})月(\d{1,2})')
        postponed_date_compile = re.compile(r'(【.+月(追加再販|延期)分?】)')
        new_release = "【新作】"

        for product in products:
            for compile_str in self.compiled_break_strs:
                if re.match(compile_str, product.text) is not None:
                   return product_list

            product_name = product.text
            # "【新作】"表記の削除
            if product_name.find(new_release) == 0:
                product_name = product_name.replace(new_release,"")

            date_param = re.match(date_compile, product_name)
            if date_param is not None:
                # 日付なら出荷日を更新
                date = "{:04d}/{:02d}/{:02d}".format(self.date.year,int(date_param.group(1)), int(date_param.group(2)))
                product_list[date] = [] 
            else:
                # 延期や追加の表記削除
                match = re.search(postponed_date_compile, product_name)
                if match is not None:
                    product_name = product_name.replace(match.group(1),"")

                brand_name = self.get_brandname(product_name)                
                product_array = product_list[date]
                product_array.append({'name': product_name, 'brand': brand_name})
                product_list[date] = product_array
        return product_list


