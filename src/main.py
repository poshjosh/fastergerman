import logging.config
import tkinter as tk

from fastergerman.app import App
from fastergerman.config import AppConfig
from fastergerman.file import load_yaml
from fastergerman.ui import DesktopGameUI

if __name__ == "__main__":
    root = tk.Tk()

    logging.config.dictConfig(load_yaml('resources/config/logging.yaml'))
    app_config = AppConfig(load_yaml('resources/config/app.yaml'))

    ui = DesktopGameUI(root, app_config)

    App.add_shutdown_callback(ui.close_window)

    root.protocol("WM_DELETE_WINDOW", ui.close_window)

    root.mainloop()
