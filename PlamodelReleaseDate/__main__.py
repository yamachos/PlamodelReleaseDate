import sys
from datetime import datetime
from pathlib import Path

import tkinter

from controller.MainWindow import Controller
from model.Okichan import Model
from view.MainWindow import View 
from resource.settings import calendars

def main():
    #name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    # window = tkinter.Tk()
    # view = View(master=window)
    #model = Model()
    # Controller(model=model, view=view)
    # window.mainloop()
    model = Model()
    now = datetime.now()
    for calendar in calendars:
        url = model.get_url(now.year, now.month)
        #print(url)
        res = model.request_page( url )
        if res is not None:
            product_list = model.get_product_list( url, res.text )
            filtering_products = model.filtering_products( product_list, calendar['filter'], True)
            model.update_calendar( calendar['url'], filtering_products )

if __name__ == "__main__":
    main()
