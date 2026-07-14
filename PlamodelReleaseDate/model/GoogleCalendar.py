import os
import sys
sys.path.append('..')
from model import Project

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendar:
    def __init__(self):
        self.service = None
        pass

    # Google Calendar APIサービスを取得する
    def get_service(self):
        if( self.service is not None):
            return self.service
        token_path = Project.get_cache_path() / 'token.json'
        credential_path = Project.get_project_path() / 'resource' / 'credential.json'
        SCOPES = ["https://www.googleapis.com/auth/calendar"]
        creds = None
        # ユーザーのアクセスとリフレッシュトークンを格納するtoken.jsonファイルが存在する場合、token.jsonを使用して認証する。
        os.makedirs(Project.get_cache_path(), exist_ok=True)
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # 有効な資格情報がない場合、ユーザーにログインさせます。
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credential_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # 次回実行のために資格情報を保存する。※二回目以降の実行では認証がスキップされる。
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return self.service
        except HttpError as error:
            print(f"サービスの取得中にエラーが発生しました: {error}")
            return None

    # Google Calendarのイベントを取得する
    def get_events(self, start_time : str, end_time : str, calendar_id : str = 'primary'):
        try:
            service = self.get_service()
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            return events
        except HttpError as error:
            print(f"イベントの取得中にエラーが発生しました: {error}")
            return None

    # Google Calendarにイベントを作成する
    def insert_event(self, summary : str, description : str, start_time : str, end_time : str, calendar_id : str = 'primary'):
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'date': start_time,
                'timeZone': 'Asia/Tokyo',
            },
            'end': {
                'date': end_time,
                'timeZone': 'Asia/Tokyo',
            },
        }
        try:
            service = self.get_service()
            created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"イベントが作成されました: {created_event.get('htmlLink')}")
        except HttpError as error:
            print(f"イベントの作成中にエラーが発生しました: {error}")   

   
    # Google Calendarのイベントを更新する
    def update_event(self, event_id : str, summary : str, start_time : str, end_time : str, description : str = None, calendar_id : str = 'primary'):
        event = {
            'summary': summary,
            'start' : {
                'dateTime': start_time,
                'timeZone': 'Asia/Tokyo'
            },
            'end' : {
                'dateTime': end_time,
                'timeZone': 'Asia/Tokyo'
            }
        }
        if(description is not None):
            event['description'] = description
 
        try:
            service = self.get_service()
            updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
            print(f"イベントが更新されました: {updated_event.get('htmlLink')}")
        except HttpError as error:
            print(f"イベントの更新中にエラーが発生しました: {error}")

    # Google Calendarのイベントを削除する
    def delete_event(self, event_id, calendar_id='primary'):
        try:
            service = self.get_service()
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            print(f"イベントが削除されました: {event_id}")
        except HttpError as error:
            print(f"イベントの削除中にエラーが発生しました: {error}")    

    # Google Calendarのイベントをパッチする
    def patch_event_description(self, event_id, description, calendar_id='primary'):
        updates = {
            'description': description
        }
        try:
            service = self.get_service()
            updated_event = service.events().patch(calendarId=calendar_id, eventId=event_id, body=updates).execute()
            print(f"イベントが更新されました: {updated_event.get('htmlLink')}")
        except HttpError as error:
            print(f"イベントの更新中にエラーが発生しました: {error}")