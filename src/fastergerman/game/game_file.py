import dataclasses
import logging
import os
from typing import Union

from fastergerman.file import create_file, read_content, write_content, write_json, read_json, \
    delete_file, delete_dir
from fastergerman.game import Game

logger = logging.getLogger(__name__)

class GameFile:
    def __init__(self, app_dir: str):
        app_dir = os.path.expanduser(os.path.expandvars(app_dir))
        data_dir = os.path.join(app_dir, "data")
        if os.path.exists(data_dir) is False:
            os.makedirs(data_dir)
        self.__game_to_load_file = os.path.join(data_dir, "game-to-load.txt")
        self.__games_dir = os.path.join(data_dir, "games")

    def exists(self, game_name: str) -> bool:
        return os.path.exists(self._get_game_file_path(game_name))

    def load_game(self, game_name: str or None = None) -> Game:
        logger.debug(f"Loading game: {game_name}")
        new_game_to_load = True
        if not game_name:
            new_game_to_load = False
            game_name = self.read_game_to_load()
        path = self._get_game_file_path(game_name)
        if os.path.exists(path) is False:
            raise FileNotFoundError(f"Game file not found: {path}")
        game_dict = read_json(path)
        if not game_dict:
            raise FileNotFoundError(f"Game file is empty: {path}")
        if new_game_to_load is True:
            self.save_game_to_load(game_name)
        return Game.of_dict(game_dict)
    
    
    def save_game(self, game: Game):
        game_name = game.name
        logger.debug(f"Saving game: '{game_name}' = {game}")
        if not game_name:
            raise ValueError("No game name provided.")
        game_dict = dataclasses.asdict(game)
        if len(game_dict) == 0:
            return False
        self.save_game_to_load(game_name)
        self._save_json(game_dict, self._get_game_file_path(game_name))
        return True
    
    
    def delete_game(self, game_name: str):
        logger.debug(f"Deleting game: {game_name}")
        if not game_name:
            raise ValueError("No game name provided.")
        self._delete_from_game_to_load(game_name)
        delete_dir(self._get_game_dir_path(game_name))
    
    
    def get_game_names(self):
        if not os.path.exists(self._get_games_dir_path()):
            return []
        def format_for_sorting(fname):
            return os.path.getmtime(os.path.join(self._get_games_dir_path(), fname))
        game_names = os.listdir(self._get_games_dir_path())
        game_names.sort(key=format_for_sorting, reverse=True) # most recent first
        return game_names

    def read_game_to_load(self, result_if_none: str or None = None) -> Union[str, None]:
        if not os.path.exists(self._get_game_to_load_file_path()):
            return result_if_none
        game_to_load = read_content(self._get_game_to_load_file_path())
        return game_to_load if game_to_load else result_if_none

    def save_game_to_load(self, game_name: str):
        if not os.path.exists(self._get_game_to_load_file_path()):
            create_file(self._get_game_to_load_file_path())
            logger.debug("Created: %s", self._get_game_to_load_file_path())
        write_content(game_name, self._get_game_to_load_file_path())
        logger.debug(f"Written {game_name} to {self._get_game_to_load_file_path()}")

    @staticmethod
    def _save_json(json, path):
        if not os.path.exists(path):
            create_file(path)
            logger.debug(f"Created: {path}")
        write_json(json, path)
        logger.debug(f"Written {json}\nto {path}")

    def _get_game_file_path(self, game_name: str):
        return os.path.join(self._get_game_dir_path(game_name), "data.json")

    def _get_game_dir_path(self, game_name: str) -> str:
        return os.path.join(self._get_games_dir_path(), game_name)

    def _delete_from_game_to_load(self, game_name: str):
        game_to_load = self.read_game_to_load()
        if game_to_load == game_name:
            game_names = self.get_game_names()
            if game_name in game_names:
                game_names.remove(game_name)
            if len(game_names) > 0:
                self.save_game_to_load(game_names[0])
            else:
                delete_file(self._get_game_to_load_file_path())
    
    def _get_game_to_load_file_path(self) -> str:
        return self.__game_to_load_file

    def _get_games_dir_path(self) -> str:
        return self.__games_dir
