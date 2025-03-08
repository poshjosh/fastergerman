import logging.config
import tkinter as tk

from fastergerman.ui import DesktopApp

if __name__ == "__main__":

    app = DesktopApp(tk.Tk())
    logging.config.dictConfig(app.logging_config.to_dict())

    app.start()
