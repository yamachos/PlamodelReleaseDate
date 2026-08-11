# python
import os
import requests
from datetime import date, datetime, timezone, timedelta
import json
import hashlib
from pathlib import Path

from abc import ABCMeta, abstractmethod
from typing import final

#
from model.GoogleCalendar import GoogleCalendar

#
from model import Project


class ModelBase(metaclass=ABCMeta):

    DEFAULT_DATE = date(2026, 1, 1)
    EVENT_TITLE_POSTFIX = "発売予定"
    CACHE_FILE_POSTFIX = ".json"

    # constractor
    def __init__(self, now: datetime):
        self.date = now
        self.calendar = GoogleCalendar()

    #
    @final
    def set_release_date(self, date: datetime):
        self.date = self.date.replace(year=date.year, month=date.month, day=1)

    #
    @final
    def get_release_date(self) -> date:
        return self.date

    # 指定した年と月からURLを生成する
    @abstractmethod
    def get_url(self) -> str:
        pass

    # 指定したURLからページを取得する
    def request_page(self, url: str) -> requests.Response:
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res
        except requests.RequestException as e:
            return None

    # キャッシュファイル名を生成する
    @final
    def make_cache_filename(self, calendar_id: str, date: datetime) -> Path:
        cache_path = (
            Project.get_cache_path() / str(date.year) / str(date.month).zfill(2)
        )
        os.makedirs(cache_path, exist_ok=True)
        hash_base = calendar_id + date.strftime("%Y%m%d")
        hash = hashlib.sha256(hash_base.encode("utf-8"))
        return cache_path / (hash.hexdigest() + self.CACHE_FILE_POSTFIX)

    # 日付けからファイル名を生成し商品キャッシュファイルを書き込む
    @final
    def write_cache_file(self, calendar_id: str, date: datetime, products: dict):
        with open(
            self.make_cache_filename(calendar_id, date), "w", encoding="utf-8"
        ) as f:
            json.dump(products, f, ensure_ascii=False, indent=4)

    # カレンダーのイベントタイトルを生成する
    @final
    def make_event_title(self, title: str, date: datetime) -> str:
        # return date.strftime('%m/%d') + self.EVENT_TITLE_POSTFIX
        return title

    def make_event_hash_key(self, title: str, date: datetime) -> str:
        return title + date.strftime("%Y%m%d")

    # 更新日時の月のイベントをカレンダーから取得する
    @final
    def get_event_list(self, calendar_id: str, modified: date):
        jst = timezone(timedelta(hours=9))
        dt_base = datetime(
            modified.year,
            modified.month,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=jst,
        )
        start_date = dt_base.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_date = (
            (dt_base + timedelta(days=32)).replace(day=1) + timedelta(seconds=-1)
        ).strftime("%Y-%m-%dT%H:%M:%S%z")
        events = self.calendar.get_events(
            calendar_id=calendar_id, start_time=start_date, end_time=end_date
        )
        # タイトルからイベントデータを検索するためのハッシュを作成
        event_hash = {}
        for event in events:
            date = datetime.strptime(event["start"]["date"], "%Y-%m-%d")
            event_hash[self.make_event_hash_key(event["summary"], date)] = event
        return event_hash

    #
    @final
    def filtering_products(
        self, product_list: dict[list[dict]], filters: list, copying=False
    ) -> dict[list[dict]]:
        result = {}
        for date in product_list:
            for product in product_list[date]:
                if product["brand"] in filters:
                    if date not in result:
                        result[date] = []
                    result[date].append(product["name"])
        return result

    # google カレンダーに発売リストと登録
    @final
    def update_calendar(
        self, calendar_title: str, calendar_id: str, product_list: dict[list[str]]
    ):
        old_products = {}
        insert_products = []
        update_products = []
        ignore_products = []
        event_hash = {}
        modified = None

        event_hash = self.get_event_list(calendar_id, self.date)
        for date_str in product_list.keys():
            key = self.make_event_hash_key(
                calendar_title, datetime.strptime(date_str, "%Y-%m-%d")
            )
            if key in event_hash:
                if product_list[date_str] != event_hash[key]["description"].split("\n"):
                    # print("update calendar: " + date_str)
                    self.calendar.patch_event_description(
                        calendar_id=calendar_id,
                        event_id=event_hash[key]["id"],
                        description="\n".join(product_list[date_str]),
                    )
                del event_hash[key]
            else:
                # print("insert calendar: " + date_str)
                start_date = datetime.strptime(date_str, "%Y-%m-%d")
                end_date = start_date + timedelta(days=1)
                self.calendar.insert_event(
                    calendar_id=calendar_id,
                    summary=calendar_title,
                    description="\n".join(product_list[date_str]),
                    start_time=start_date.strftime("%Y-%m-%d"),
                    end_time=end_date.strftime("%Y-%m-%d"),
                )

        for key in event_hash:
            self.calendar.delete_event(
                calendar_id=calendar_id, event_id=event_hash[key]["id"]
            )

    # 製品リストを取得する
    @abstractmethod
    def get_product_list(html: str):
        pass
