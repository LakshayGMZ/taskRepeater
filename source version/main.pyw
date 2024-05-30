import os.path
from tkinter import *
from mainApp import MainApp

if __name__ == '__main__':
    if not os.path.exists("actions"):
        os.makedirs("actions")

    root = Tk()
    app = MainApp(root)
    app.run()
