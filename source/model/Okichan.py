# python standard
import sys
import re
from datetime import datetime
from typing import List
import traceback

# 3rdparty
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
#
from model.ModelBase import ModelBase
from model import Project

class Okichan(ModelBase):
    BRANDS = {
    #'Figure-rise Standard Amplified' : 'FrS Amplified',
    #'Figure-rise Standard': 'FrS',
    'MGSD': 'MGSD',
    'HG': 'HG',
    'オプションパーツセット ガンプラ': 'HG',
    'MG': 'MG',
    'RG': 'RG',
    'PG': 'PG',
    'SD': 'SD',
    'ENTRY GRADE' : 'EG',
    'EG' : 'EG',
    'RE/100': 'RE/100',
    'FULL MECHANICS': 'FM',
    'FM': 'FM',
    '30 MINUTES MISSONS' : '30MM',
    '30MM' : '30MM',
    '30 MINUTES SISTERS' : '30MS',
    '30MS' : '30MS',
    '30 MINUTES FANTASY' : '30MF',
    '30MF' : '30MF',
    '30 MINUTES PREFARENS' : '30MP',
    '30MP' : '30MP',
    'etc.' : 'etc.',
    }

    MONTH_ENGLISH_STRINGS = [
        'january',
        'february',
        'march',
        'april',
        'may',
        'june',
        'july',
        'august',
        'september',
        'october',
        'november',
        'december'
    ]

    SCRAPING_PAGE_URL_BASE = 'https://kaigoshinootakunaburogu.com/gunpla-resale-calendar-'

    BREAK_PRODUCT_LIST_STRINGS = [
        r'.*【再販中止】になったガンプラ.*',
        r'\d+年\d+月のガンプラ再販キット【注目ランキング】',
        r'\d+年ガンプラ再販スケジュールまとめ',
        r'ガンプラ再販アンケート'
    ]

    def __init__(self, now: datetime ):
        super().__init__( now )

        self.brands = []
        self.brands = self.get_brand_list()

        self.compiled_break_strs = []
        for break_str in self.BREAK_PRODUCT_LIST_STRINGS:
            self.compiled_break_strs.append( re.compile( break_str ) )
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument( '--disable-popup-blocking' )
            options.add_argument( '--disable-infobars' )
            if sys.platform == "win32":
                self.driver = webdriver.Chrome( options = options )
            else:
                driver_path = Project.get_project_path() / 'chromedriver' / 'chromedriver'
                # print( driver_path )
                service = webdriver.ChromeService( executable_path = driver_path )
                self.driver = webdriver.Chrome( service = service, options = options )

        except WebDriverException:
            traceback.print_exc()
            print('WebDriverの通信エラーが発生しました。インターネット接続を確認してください。')

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    # 製品名からブランド名を取得する 
    def get_brandname(self, name: str) -> str:
        for key, value in self.BRANDS.items():
            if key in name:
                return value
        return self.BRANDS['etc.']

    # 製品ブランド一覧の初期化
    def get_brand_list(self) -> list:
        if len(self.brands) > 0:
            return self.brands 

        brand_hash = {}
        for brand in self.BRANDS.values():
            brand_hash[brand] = True

        for brand in brand_hash.keys():
            self.brands.append(brand)

        return self.brands

    # 指定した年と月からURLを生成する
    def get_url( self ) -> str:
        if self.date.month < 1 or self.date.month > 12:
            raise ValueError('Month must be between 1 and 12')
        month_name = self.MONTH_ENGLISH_STRINGS[self.date.month - 1]
        return f'{self.SCRAPING_PAGE_URL_BASE}{str(self.date.year)}{month_name}'

    def request_page( self, url: str ):
        try:
            #self.driver.implicitly_wait( 10 )
            self.driver.get( url )
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'toc-content')))
            except TimeoutException:
                print('条件を満たせませんでした')
        except WebDriverException:
            print('WebDriverの通信エラーが発生しました。インターネット接続を確認してください。')

    # 製品リストを取得する
    def get_product_list(self, filters: List[str]):
        product_list = {}
        product_list.clear()

        date_compile = re.compile(r'(\d{1,2})月(\d{1,2})')
        postponed_date_compile = re.compile(r'(【.+月(追加再販|延期)分?】)')
        new_release = '【新作】'

        toc = self.driver.find_element(By.XPATH, '//div[@class="toc-content"]/ol')
        rows = toc.find_elements(By.XPATH, 'li')
        for row in rows:
            date_element = row.find_element(By.XPATH, 'a') 
            #print( date_element.text )
            name_elements = row.find_elements(By.XPATH, 'ol/li/a')
            #print( [n.text for n in name_elements] )
            # 日付のリンクが中断リストの文言と合致したら処理終了
            for compile_str in self.compiled_break_strs:
                if re.match(compile_str, date_element.text) is not None:
                    return product_list
            date_param = re.match(date_compile, date_element.text)
            if date_param is not None:
                date = '{:04d}-{:02d}-{:02d}'.format(self.date.year, int(date_param.group(1)), int(date_param.group(2)))
                for name_element in name_elements:
                    name = name_element.text
                    # '【新作】'表記の削除
                    if name.find(new_release) == 0:
                        name = name.replace(new_release,'')
                    else:
                        # 延期や追加の表記削除
                        match = re.search(postponed_date_compile, name)
                        if match is not None:
                            name = name.replace(match.group(1), '')

                    brand_name = self.get_brandname(name)
                    if brand_name in filters:
                        if date not in product_list:
                            product_list[date] = []
                        product_array = product_list[date]
                        product_array.append(name)
                        product_list[date] = product_array

        return product_list


