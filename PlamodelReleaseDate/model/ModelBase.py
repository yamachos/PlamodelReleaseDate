# python
import os
import requests
from datetime import date, datetime, timezone, timedelta
import json
import re
import hashlib
from pathlib import Path

from abc import ABCMeta, abstractmethod
from typing import final

#
from model import Project

class ModelBase(metaclass=ABCMeta):
    BRANDS = {
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
    "FULL MECHANICS": "FM",
    "FM": "FM",
    "30 MINUTES MISSONS" : "30MM",
    "30MM" : "30MM",
    "30 MINUTES SISTERS" : "30MS",
    "30MS" : "30MS",
    "30 MINUTES FANTASY" : "30MF",
    "30MF" : "30MF",
    "30 MINUTES PREFARENS" : "30MP",
    "30MP" : "30MP",
    "etc." : "etc.",
    }

    DEFAULT_DATE = date( 2026, 1, 1 )
    EVENT_TITLE_POSTFIX = '発売予定'
    CACHE_FILE_POSTFIX = '.json'

    # constractor
    def __init__( self ):
        self.date = self.DEFAULT_DATE
        self.brands = []
        self.brands = self.get_brand_list()

    # 製品名からブランド名を取得する 
    @final
    def get_brandname(self, name: str) -> str:
        for key, value in self.BRANDS.items():
            if key in name:
                return value
        return self.BRANDS['etc.']

    # 製品ブランド一覧の初期化
    @final
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
    @abstractmethod
    def get_url( year: int, month: int ):
        pass

    # 指定したURLからページを取得する
    @final
    def request_page( self, url: str ) -> requests.Response:
        try:
            res = requests.get( url )
            res.raise_for_status()
            return res
        except requests.RequestException as e:
            return None

    # キャッシュファイル名を生成する
    @final
    def make_cache_filename( self, calendar_id: str, date: datetime ) -> Path:
        cache_path = Project.get_cache_path() / str(date.year) / str(date.month).zfill(2)
        os.makedirs( cache_path, exist_ok = True )
        hash_base = calendar_id + date.strftime('%Y%m%d')
        hash = hashlib.sha256(hash_base.encode('utf-8'))
        return cache_path / (hash.hexdigest() + self.CACHE_FILE_POSTFIX)

    # 日付けからファイル名を生成し商品キャッシュファイルを書き込む
    @final
    def write_cache_file( self, calendar_id: str, date: datetime, products: dict ):
        with open( self.make_cache_filename( calendar_id, date ), 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)

    # カレンダーのイベントタイトルを生成する
    @final
    def make_event_title(self, date: datetime) -> str:
        return date.strftime('%m/%d') + self.EVENT_TITLE_POSTFIX

    # 更新日時の月のイベントをカレンダーから取得する
    @final
    def get_event_list( self, calendar_id : str, modified : date ):
            jst = timezone(timedelta(hours=9))
            dt_base = datetime( modified.year, modified.month, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=jst)
            start_date = dt_base.strftime('%Y-%m-%dT%H:%M:%S%z')
            end_date = ((dt_base + timedelta(days=32)).replace(day=1) + timedelta(seconds=-1)).strftime('%Y-%m-%dT%H:%M:%S%z')
            events = self.calendar.get_events(
                calendar_id = calendar_id,
                start_time = start_date,
                end_time = end_date
            )
            # タイトルからイベントデータを検索するためのハッシュを作成
            event_hash = {}
            for event in events:
                event_hash[event['summary']] = event
            return event_hash

    #     
    @final
    def filtering_products( self, product_list :dict[list[dict]], filters : list, copying=False ) ->dict[list[dict]]:
        result = {}
        for date in product_list:
            for product in product_list[date]:
                if product['brand'] in filters:
                    if date not in result:
                        result[date] = []
                    result[date].append(product['name'])
        return result

    # google カレンダーに発売リストと登録
    @final
    def update_calendar( self, calendar_id : str, product_list : dict[list[str]] ):
        old_products = {}
        insert_products = []
        update_products = []
        ignore_products = []
        event_hash = {}
        modified = None
        for date_str in product_list.keys():
            old_products_filename = self.make_cache_filename( calendar_id, datetime.strptime(date_str, '%Y/%m/%d'))
            file = Path(old_products_filename)
            if( file.exists() ):
                with file.open( 'r', encoding='utf-8') as f:
                    old_products = json.load( f )
                if( old_products != product_list[date_str] ):
                    #print("update calendar: " + date_str)
                    update_products.append(date_str)
                else:
                    ignore_products.append(date_str)
                modified = date_str
            else:
                #print("insert calendar: " + date_str)
                insert_products.append(date_str)

        # 更新が必要なので該当月のイベントを取得する
        if modified is not None:
            event_hash = self.get_event_list( calendar_id, datetime.strptime(modified, '%Y/%m/%d') )
            # タイトルからイベントデータを検索するためのハッシュを作成
        
        # 更新処理
        if len(update_products) > 0:
            #with open( 'events.json', 'w', encoding='utf-8') as f:
            #    json.dump(events, f, ensure_ascii=False, indent=4)

            for date_str in update_products:
                # すでに同じタイトルの見出しがある場合は内容だけを更新する
                summary = self.make_event_title( datetime.strptime( date_str, '%Y/%m/%d') )
                if summary in event_hash:
                    self.calendar.patch_event_description(
                        calendar_id = calendar_id,
                        event_id = event_hash[summary]['id'],
                        description = '\n'.join(product_list[date_str])
                    )
                    del event_hash[summary]
                    self.write_cache_file( calendar_id, datetime.strptime( date_str, '%Y/%m/%d' ), product_list[date_str])
                else:
                    # なければ予定を追加
                    insert_products.append(date_str)

        if len(insert_products) > 0:
            for date_str in insert_products:
                start_date = datetime.strptime(date_str, '%Y/%m/%d')
                end_date = start_date + timedelta(days=1)
                self.calendar.insert_event(
                    calendar_id = calendar_id,
                    summary = self.make_event_title(start_date),
                    description = '\n'.join(product_list[date_str]),
                    start_time = start_date.strftime('%Y-%m-%d'),
                    end_time = end_date.strftime('%Y-%m-%d')
                )

                self.write_cache_file( calendar_id, start_date, product_list[date_str] )

        if len(ignore_products) > 0:
            for date_str in ignore_products:
                # すでに同じタイトルの見出しがある場合は内容だけを更新する
                summary = self.make_event_title( datetime.strptime( date_str, '%Y/%m/%d') )
                if summary in event_hash:
                    del event_hash[summary]

        # イベントの更新が終わったあともカレンダーから所得したイベントが残っている場合は削除対象
        if len(event_hash) > 0:
            summary_list = []
            for date_str in ignore_products:
                summary_list.append( self.make_event_title( datetime.strptime( date_str, '%Y/%m/%d' ) ) )
 
            for summary in event_hash:
                if summary not in summary_list:
                    self.calendar.delete_event(
                        calendar_id = calendar_id,
                        event_id = event_hash[summary]['id']
                    )
                    delete_filename = self.make_cache_filename( calendar_id, datetime.strptime( event_hash[summary]['start']['date'], '%Y-%m-%d' ) )
                    file = Path( delete_filename )
                    if( file.exists() ):
                        file.unlink()

    # 製品リストを取得する
    @abstractmethod
    def get_product_list( html: str ):
        pass

