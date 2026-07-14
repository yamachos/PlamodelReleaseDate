import sys
sys.path.append('..')

from model.Okichan import Model
from view.MainWindow import View 
from resource.settings import calendars

class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.view.receive_button.config(command = lambda :self.exec_scraping(self.view.year_combobox.get(), self.view.month_combobox.get()))
        self.view.filter.configure(choices=self.model.get_brand_list(), command=lambda :self.change_filter_state())
        self.view.create_button.config(command = lambda :self.create_schedule(calendars[0]['url'], self.view.products.get_checked()))
        self.view.products.config(yscrollcommand=self.view.ybar.set)
        self.view.ybar.config(command=self.ybar)
        self.product_list = {}
        self.view_list = None

    # チェックボックスツリービューのスクロールバー処理
    def ybar(self, *args):
        self.view.products.yview(*args)

    # チェックボックスツリービューから指定日のアイテムIDを返す
    def get_view_date_id(self, date ):
        parent_iids = self.view.products.get_children()
        for parent_iid in parent_iids:
            parent_item = self.view.products.item(parent_iid)
            if date == parent_item['text']:
                return parent_iid
        return None
    
    # チェックボックスツリービューから発売予定の商品一覧を返す
    def get_view_product_list(self):
        product_list = {}
        parent_iids = self.view.products.get_children()
        for parent_iid in parent_iids:
            parent_item = self.view.products.item(parent_iid)
            iids = self.view.products.get_children(parent_iid)
            product_array = []
            for iid in iids:
                item = self.view.products.item(iid)
                product_array.append({ 'name': item['text'], 'id': iid })
            product_list[parent_item['text']] = product_array
#        print( product_list )
        return product_list

    # 日付とタイトルからチェックボックスツリービューのアイテムIDを返す
    def get_item_id( self, date, name ):
        if self.view_list == None:
            self.view_list = self.get_view_product_list()
        if date in self.view_list:
            for product in self.view_list[date]:
                if product['name'] == name:
                    return product['id']
        return None

    # ブランドフィルターのチェックが切り替わったときの処理
    def change_filter_state(self):
        checked_items = self.view.filter.get_checkeditems()
        self.view_list = None
        for date in self.product_list:
            for product in self.product_list[date]:
                iid = self.get_item_id(date, product['name'] )
                if iid != None:
                    if product['brand'] not in checked_items:
                        parent_id = self.view.products.parent( iid )
                        self.view.products.delete( iid )
                        product['id'] = ''
                        if len(self.view.products.get_children(parent_id)) == 0:
                            self.view.products.delete( parent_id )
                else:
                    if product['brand'] in checked_items:
                        iid = self.get_view_date_id( date )
                        if iid == None:
                            iid = self.view.products.insert(parent='', index='end', iid = None,text= date )
                            self.view.products.change_state(iid, "checked")
                        child_iid = self.view.products.insert(
                            parent=iid,
                            index='end',
                            iid = None,
                            text= product['name'],
                        )
                        self.view.products.change_state(child_iid, "checked")
                        product['iid'] = child_iid

    # チェックボックスツリービューに商品一覧を登録する
    def set_product_list(self, product_list=None):

        if product_list is not None:
            for date in product_list.keys():
                parent_iid = self.view.products.insert(parent='', index='end', iid = None,text= date )
                self.view.products.change_state(parent_iid, "checked")
                for product in product_list[date]:
                    if( 'brand' not in product):
                        product['brand'] = ''
                    child_iid = self.view.products.insert(
                        parent=parent_iid,
                        index='end',
                        iid = None,
                        text= product['name'],
                    )
                    self.view.products.change_state(child_iid, "checked")
                    product['iid'] = child_iid
            self.view.products.expand_all()

    # viewから年と月を取得し、modelにスクレイピングを依頼、取得した商品一覧をviewに登録する
    def exec_scraping(self, year: int, month: int):
        url = self.model.get_url(year, month)
        #print(url)
        res = self.model.request_page( url )
        if res is not None:
            #self.view.url_history.append(url)
            self.product_list = self.model.get_product_list( url, res.text )
            self.set_product_list(self.product_list)
#            print( self.product_list)
        else:
            self.view.show_error("Error", f"request page not found\n{url}")

    # viewから選択された商品一覧を取得し、modelにGoogle Calendarのスケジュール作成を依頼する
    def create_schedule(self, calendar_id : str, selected_iid: list):
        product_list = {}
        for iid in selected_iid:
            product = self.view.products.item(iid, "text")
            date_iid = self.view.products.parent(iid)
            date = self.view.products.item(date_iid, "text")
            if date not in product_list:
                product_list[date] = []
            product_list[date].append(product)
        self.model.update_calendar( calendar_id, product_list )
