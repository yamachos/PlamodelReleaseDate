import tkinter as tk

class ChecklistBox(tk.Frame):
    def __init__(self, parent, choices=None, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.vars = []

        self.create_checkboxes(choices)

    def create_checkboxes(self, choices=None,command=None):
        if choices is None:
            return
        # Clear existing checkboxes
        for cb in self.winfo_children():
            cb.destroy()
        bg = self.cget("background")
        for choice in choices:
            var = tk.StringVar(value=choice)
            self.vars.append(var)
            cb = tk.Checkbutton(self, var=var, text=choice,
                            onvalue=choice, offvalue="",
                            anchor=tk.W, width=20, background=bg,
                            relief=tk.FLAT, highlightthickness=0,
                            command=command
            )
            cb.pack(side="top", fill=tk.X, anchor=tk.W)

    def configure(self, choices=None, command=None, **kwargs):
        self.create_checkboxes(choices, command)

    def get_checkeditems(self):
        values = []
        for var in self.vars:
            value =  var.get()
            if value:
                values.append(value)
        return values