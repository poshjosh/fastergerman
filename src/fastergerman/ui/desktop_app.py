import tkinter as tk
from fastergerman.app import App
from fastergerman.ui import DesktopGameUI


class DesktopApp(App):
    def __init__(self, root: tk.Tk, app_config_path: str = None, logging_config_path: str = None):
        super().__init__(app_config_path, logging_config_path)

        self.ui = DesktopGameUI(root, self.config)

        App.add_shutdown_callback(self.ui.close_window)

        self.root = root
        root.protocol("WM_DELETE_WINDOW", self.ui.close_window)

    def start(self):
        self.root.mainloop()
