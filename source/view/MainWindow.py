import sys
sys.path.append('..')
import datetime

import tkinter as tk
import tkinter.ttk as ttk
from ttkwidgets.checkboxtreeview import CheckboxTreeview

from widget.CheckListBox import ChecklistBox

class View(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.url_history = []
        self.master.title("Plamodel Release Date")
        self.master.geometry("768x432")
        self.create_widgets()

    def create_widgets(self):
        url_frame = tk.Frame(self.master)
        url_frame.grid(row=0, column=0, padx=2, pady=2, sticky=tk.EW)
        product_frame = tk.Frame(self.master)
        product_frame.grid(row=1, column=0, padx=2, pady=2, sticky=tk.NSEW)
        create_frame = tk.Frame(self.master)
        create_frame.grid(row=2, column=0, padx=2, pady=2, sticky=tk.EW)

        # Configure the grid to allow frame1 to expand horizontally
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)

        label1 = tk.Label(url_frame, text="Request year/month:")
        label1.pack(side=tk.LEFT, padx=2, pady=2)

        #self.entry = AutocompleteEntry(url_frame,completevalues=self.url_history)
        #self.entry.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        now = datetime.datetime.now()
        #print(now.strftime("%Y-%m-%d %H:%M:%S"))

        self.year_combobox = ttk.Combobox(url_frame, text="Year:", justify=tk.RIGHT)
        self.year_combobox.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.BOTH, expand=True)
        self.year_combobox['values'] = (str(now.year - 1), str(now.year), str(now.year + 1))
        self.year_combobox.current(1)  # Set the default selection to the current year

        label2 = tk.Label(url_frame, text="/")
        label2.pack(side=tk.LEFT, padx=2, pady=2)

        self.month_combobox = ttk.Combobox(url_frame, text="Month:", justify=tk.RIGHT)
        self.month_combobox.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.BOTH, expand=True)
        self.month_combobox['values'] = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12")
        self.month_combobox.current(now.month - 1)  # Set the default selection to the current month

        self.receive_button = tk.Button(url_frame, text="Get page data")
        self.receive_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.BOTH, expand=True)

        self.group_box = tk.LabelFrame(product_frame, text="Filter", padx=2, pady=2)
        self.group_box.pack(padx=2, pady=2, fill="both", anchor=tk.N, side=tk.LEFT)

        self.filter = ChecklistBox(self.group_box)
        self.filter.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.BOTH)

        self.products = CheckboxTreeview(product_frame)
        self.products.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.BOTH, expand=True)

        self.ybar = tk.Scrollbar(product_frame, orient=tk.VERTICAL)
        self.ybar.pack(side=tk.RIGHT, fill=tk.Y)

        self.create_button = tk.Button(create_frame, text="Create")
        self.create_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

    def show_error(self, title, message):
        tk.messagebox.showerror(title, message)
