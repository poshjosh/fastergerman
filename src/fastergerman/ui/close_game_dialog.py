import logging
from tkinter import simpledialog
from typing import Callable

from fastergerman.i18n import I18n, SAVE_GAME_AS, PLEASE_ENTER_NAME

logger = logging.getLogger(__name__)


class CloseGameDialog:
    def __init__(self, lang_code: str):
        self.title = I18n.translate(lang_code, SAVE_GAME_AS)
        self.prompt = I18n.translate(lang_code, PLEASE_ENTER_NAME)

    def ask(self, value: str, on_ok: Callable[[str], None]):
        game_name = simpledialog.askstring(self.title, self.title, initialvalue=value.strip())
        logger.debug(f"Entered game name: {game_name}")
        if game_name is None:
            return
        while not game_name.strip():
            game_name = simpledialog.askstring(self.title, self.prompt)
            logger.debug(f"Entered game name: {game_name}")
            if game_name is None:
                return

        on_ok(game_name)

