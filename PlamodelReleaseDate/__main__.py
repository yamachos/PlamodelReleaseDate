import time
from datetime import datetime, timedelta

# import tkinter

# from controller.MainWindow import Controller
from model.Okichan import Okichan
from model.Kounoudo import Kounoudo

# from view.MainWindow import View
from res.settings import calendars, Model


def main():
    # name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    # window = tkinter.Tk()
    # view = View(master=window)
    # model = Model()
    # Controller(model=model, view=view)
    # window.mainloop()

    month = 0
    now = datetime.now()
    while month != now.month:
        used_class = ""
        model = None
        for calendar in calendars:
            print(f"Processing calendar: {calendar.title}")
            if used_class != calendar.used_class:
                if calendar.used_class == Model.OKICHAN:
                    if model is not None:
                        model.close()
                    model = Okichan(now)
                elif calendar.used_class == Model.KOUNOUDO:
                    if model is not None:
                        model.close()
                    model = Kounoudo(now)
                else:
                    raise ValueError(f"Unknown used_class: {calendar.used_class}")
                used_class = calendar.used_class
                time.sleep(3)
                url = model.get_url()
                # print(url)
                model.request_page(url)

            product_list = model.get_product_list(calendar.filters)
            # print( product_list )
            model.update_calendar(calendar.title, calendar.url, product_list)

        month = now.month
        now += timedelta(days=7)
        model.close()


if __name__ == "__main__":
    main()
