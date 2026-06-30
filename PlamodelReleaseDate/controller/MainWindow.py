import sys

sys.path.append('..')
from model.MainWindow import Model
from view.MainWindow import View 

class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        self.view.button.config(command = lambda :self.exec_scraping(self.view.entry.get()))


    def exec_scraping(self, url: str):
        if self.model.request_page(url):
            self.view.url_history.append(url)
            product_list = self.model.get_product_list(url, self.model.data[url])
        else:
            product_list = []
            self.view.show_error("Error", f"request page not found\n{url}")

