# python standard
import sys
import time
from datetime import datetime
from typing import List

# 3rdparty
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By

from model.ModelBase import ModelBase
from model import Project


class Kounoudo(ModelBase):
    SCRAPING_PAGE_URL_BASE = "https://hobisima.com/sc/"

    # コンストラクタ
    def __init__(self, now: datetime):
        super().__init__(now)
        self.compiled_break_strs = []
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-infobars")
            if sys.platform == "win32":
                self.driver = webdriver.Chrome(options=options)
            else:
                driver_path = (
                    Project.get_project_path() / "chromedriver" / "chromedriver"
                )
                # print( driver_path )
                service = webdriver.ChromeService(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)

        except WebDriverException:
            print(
                "WebDriverの通信エラーが発生しました。インターネット接続を確認してください。"
            )

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    # 指定した年と月からURLを生成する
    def get_url(self) -> str:
        return self.SCRAPING_PAGE_URL_BASE

    def request_page(self, url: str):
        try:
            # self.driver.implicitly_wait( 10 )
            self.driver.get(url)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, "p-calendar-main")
                    )
                )
                # remove Google AdSense elements
                self.driver.execute_script("""
                    var element = document.getElementById('google-anno-sa');
                    if (element) element.remove();
                """)
            except TimeoutException:
                print("条件を満たせませんでした")
        except WebDriverException:
            print.error(
                "WebDriverの通信エラーが発生しました。インターネット接続を確認してください。"
            )

    # 製品リストを取得する
    def get_product_list(self, filters: List[str]):
        product_list = {}
        product_list.clear()

        try:
            # 発売月クリック
            buttons = self.driver.find_elements(
                By.XPATH, '//div[@id="monthContainer"]/button'
            )
            button_text = str(self.date.year) + "年" + str(self.date.month) + "月"
            button = [b for b in buttons if b.text == button_text]
            # print( button[0].text )
            # print( button[0].get_attribute( 'className' ) )
            if (
                len(button) > 0
                and button[0].get_attribute("className").find("is-active") == -1
            ):
                ActionChains(self.driver).scroll_to_element(button[0]).perform()
                ActionChains(self.driver).move_to_element(button[0]).perform()
                time.sleep(1)
                button[0].click()
                time.sleep(1)

            # カテゴリを全部表示
            toggle = self.driver.find_element(
                By.XPATH,
                '//div[@class="filter-row series-filter"]/button[@class="btn-toggle"]',
            )
            if toggle.text == "もっと見る":
                toggle.click()
                time.sleep(1)

            # カテゴリをクリック
            for filter in filters:
                # print( filter )
                buttons = self.driver.find_elements(
                    By.XPATH, '//div[@id="seriesContainer"]/button'
                )
                # print( [b.text for b in buttons] )
                button = [b for b in buttons if b.text == filter]
                # print( button[0].text )
                # print( button[0].get_attribute( 'className' ) )

                if (
                    len(button) > 0
                    and button[0].get_attribute("className").find("is-active") == -1
                ):
                    ActionChains(self.driver).scroll_to_element(button[0]).perform()
                    ActionChains(self.driver).move_to_element(button[0]).perform()
                    time.sleep(1)
                    button[0].click()
                    time.sleep(1)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.ID, "js-calendar-main"))
                )

                rows = self.driver.find_elements(By.CLASS_NAME, "p-row")
                for row in rows:
                    date = row.find_element(
                        By.XPATH, 'div[@class="p-date-col"]/span[@class="date-num"]'
                    )
                    temp_date = date.text.split("/")
                    date_str = (
                        str(self.get_release_date().year)
                        + "-"
                        + temp_date[0].zfill(2)
                        + "-"
                        + temp_date[1].zfill(2)
                    )
                    products = row.find_elements(
                        By.XPATH,
                        'div[@class="p-items-col"]/a/div[@class="p-card"]/div[@class="p-info"]/h5[@class="p-name"]',
                    )
                    if date_str not in product_list:
                        product_list[date_str] = []

                    for product in products:
                        product_array = product_list[date_str]
                        product_array.append(product.text)
                        product_list[date_str] = product_array
        except NoSuchElementException:
            print("要素が見つかりませんでした")

        # print( product_list )

        return product_list
