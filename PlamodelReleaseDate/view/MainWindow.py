import tkinter as tk
from ttkwidgets.autocomplete import AutocompleteEntry

class View(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.url_history = []
        #self.pack()
        self.master.title("Plamodel Release Date")
        self.master.geometry("400x300")
        self.create_widgets()


    def create_widgets(self):
        frame = tk.Frame(self.master)
        frame.grid(row=0, column=0, padx=2, pady=2,sticky=tk.E+tk.W)

        # Configure the grid to allow frame1 to expand horizontally
        self.master.grid_columnconfigure(0, weight=1)

        self.label = tk.Label(frame, text="URL:")
        self.label.pack(side=tk.LEFT, padx=2, pady=5)

        self.entry = AutocompleteEntry(frame,completevalues=self.url_history)
        self.entry.pack(side=tk.LEFT, padx=2, pady=5, fill=tk.X, expand=True)

        self.button = tk.Button(frame, text="Get page data")
        self.button.pack(side=tk.LEFT, padx=2, pady=5)

    def show_error(self, title, message):
        tk.messagebox.showerror(title, message)
