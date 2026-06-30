import sys
import tkinter

from controller.MainWindow import Controller
from model.MainWindow import Model
from view.MainWindow import View 

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    window = tkinter.Tk()
    view = View(master=window)
    model = Model()
    controller = Controller(model=model, view=view)
    window.mainloop()

if __name__ == "__main__":
    main()
