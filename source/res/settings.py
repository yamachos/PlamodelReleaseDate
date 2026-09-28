from dataclasses import dataclass
from typing import List
from enum import Enum

@dataclass(frozen=True)
class CalendarSetting:
    title : str
    used_class : str
    filters : List[str]
    url : str

class Model(Enum):
    OKICHAN = 'Okichan'
    KOUNOUDO = 'Kounoudo'


calendars = [
    CalendarSetting(
        title = 'ガンプラ',
        used_class = Model.OKICHAN,
        filters = ['MGSD', 'HG', 'MG', 'RG', 'PG', 'SD', 'EG', 'RE/100', 'FM'],
        url = 'aa4ffc82cae7b1a3c87273a10e1cebaf07d3f1d1e5eb3004e8448f7b95e7d04c@group.calendar.google.com'
    ),
    CalendarSetting(
        title = '30MS/MP',
        used_class = Model.OKICHAN,
        filters = ['30MS', '30MP'],
        url = 'a26172608d3612eeeb7d862b1323ab7d10d2291bb3a586234a1ce8110e0b81eb@group.calendar.google.com'
    ),
    CalendarSetting(
        title = '30MM/MF',
        used_class = Model.OKICHAN,
        filters = ['30MM', '30MF'],
        url = 'dbc30c769fa3bf4fa73c7eb951c8e12f4a2185374f9a25198d16b36e2971a290@group.calendar.google.com'
    ),
    CalendarSetting(
       # バンダイ製品その他
        title = 'バンダイ',
        used_class = Model.OKICHAN,
        filters = ['FrS Amplified', 'FrS', 'etc.'],
        url = '5ddaedf490073d747edc8b64da13e4576f4aad0b95b747f4ccf607e1f2eaca72@group.calendar.google.com'
    ),
    CalendarSetting(
        title = 'コトブキヤ',
        used_class = Model.KOUNOUDO,
	    filters = ['メガミデバイスシリーズ', 'フレームアームズ・ガールシリーズ', '創彩少女庭園シリーズ',
                     'アルカナディアシリーズ', '無限邂逅メガロマリアシリーズ', 'グランデスケール',
                     'M.S.Gシリーズ', 'ウェポンユニット', 'バーチュアスタイル',
                     'フレームアームズ', 'HMM'
        ],
        url = '36cbdd735d66dba3ee576989e2fb7185c4cdff91424d473b4978a78ebe8f4d9a@group.calendar.google.com'
    ),
    CalendarSetting(
        title = 'カドプラ',
        used_class = Model.KOUNOUDO,
	    filters = ['KADOKAWA PLASTIC MODEL SERIES'],
        url = 'c20714fb56329a8d7cfa88255dba28c16f0041d7ccf407dec6348f3bd0ef1af7@group.calendar.google.com'
    ),
    CalendarSetting(
        title = 'グッスマ',
        used_class = Model.KOUNOUDO,
	    filters = ['MODEROID（モデロイド）', 'PLAMATEA（プラマテア）', 'PLAMAX（プラマックス）', 'Reincarnation'],
        url = '452f76091b422ae86ad72c2eb56841b8408d4b1cc397eccfa95c550a49a9b121@group.calendar.google.com'
    ),
    CalendarSetting(
        title = 'アオシマ',
        used_class = Model.KOUNOUDO,
	    filters = ['けもプラシリーズ'],
        url = 'c9325894d544c767b0d49c9ed8e2ea5b7a6b1c6756fe5f121b099a74b8098fa1@group.calendar.google.com'
    )
]
