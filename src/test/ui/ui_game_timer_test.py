import unittest
import tkinter as tk

from fastergerman.game import GameTimer
from fastergerman.ui import UIGameTimer
from test.game import GameTimerCommon


class UIGameTimerTest(GameTimerCommon.GameTimerTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _create_timer(self, interval_millis: int = 1000) -> GameTimer:
        return UIGameTimer(tk.Tk(), interval_millis)


if __name__ == '__main__':
    unittest.main()
