import dataclasses
import logging
import os
from abc import ABC, abstractmethod
from typing import Union

from fastergerman.file import create_file, read_content, write_content, write_json, read_json, \
    delete_file, delete_dir
from fastergerman.game import Game

logger = logging.getLogger(__name__)

class AbstractGameStore(ABC):
    @abstractmethod
    def exists(self, game_name: str) -> bool:
        pass

    @abstractmethod
    def load_game(self, game_name: str or None = None) -> Game:
        pass

    @abstractmethod
    def save_game(self, game: Game):
        pass

    @abstractmethod
    def read_game_to_load(self, result_if_none: str or None = None) -> Union[str, None]:
        pass

    @abstractmethod
    def load_game_names(self):
        pass

    @abstractmethod
    def delete_game(self, game_name: str):
        pass

class InMemoryGameStore(AbstractGameStore):
    def __init__(self, default_game_name: str = "default_game"):
        super().__init__()
        self.games = {}
        self.last_game = default_game_name

    def exists(self, game_name: str) -> bool:
        return game_name in self.games

    def load_game(self, game_name: str or None = None) -> Game:
        if not game_name:
            game_name = self.last_game
        return self.games.get(game_name)

    def save_game(self, game: Game):
        self.games[game.name] = game

    def read_game_to_load(self, result_if_none: str or None = None) -> Union[str, None]:
        return self.last_game if self.last_game else result_if_none

    def load_game_names(self):
        return self.games.keys()

    def delete_game(self, game_name: str):
        if game_name in self.games:
            del self.games[game_name]

class FileGameStore(AbstractGameStore):
    @staticmethod
    def of_dir(game_dir: str):
        data_dir = os.path.join(game_dir, "data")
        if os.path.exists(data_dir) is False:
            os.makedirs(data_dir)
        return FileGameStore(data_dir)

    def __init__(self, data_dir: str):
        self.__game_to_load_file = os.path.join(data_dir, "game-to-load.txt")
        self.__games_dir = os.path.join(data_dir, "games")

    def exists(self, game_name: str) -> bool:
        return os.path.exists(self._get_game_store_path(game_name))

    def load_game(self, game_name: str or None = None) -> Game:
        logger.debug(f"Loading game: {game_name}")
        new_game_to_load = True
        if not game_name:
            new_game_to_load = False
            game_name = self.read_game_to_load()
        path = self._get_game_store_path(game_name)
        if os.path.exists(path) is False:
            raise FileNotFoundError(f"Game file not found: {path}")
        game_dict = read_json(path)
        if not game_dict:
            raise FileNotFoundError(f"Game file is empty: {path}")
        if new_game_to_load is True:
            self._save_game_to_load(game_name)
        return Game.of_dict(game_dict)

    def save_game(self, game: Game):
        game_name = game.name
        logger.debug(f"Saving game: '{game_name}' = {game}")
        if not game_name:
            raise ValueError("No game name provided.")
        game_dict = dataclasses.asdict(game)
        if len(game_dict) == 0:
            return False
        self._save_game_to_load(game_name)
        self._save_json(game_dict, self._get_game_store_path(game_name))
        return True

    def delete_game(self, game_name: str):
        logger.debug(f"Deleting game: {game_name}")
        if not game_name:
            raise ValueError("No game name provided.")
        self._delete_from_game_to_load(game_name)
        delete_dir(self._get_game_dir_path(game_name))

    def load_game_names(self):
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

    def _save_game_to_load(self, game_name: str):
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

    def _get_game_store_path(self, game_name: str):
        return os.path.join(self._get_game_dir_path(game_name), "data.json")

    def _get_game_dir_path(self, game_name: str) -> str:
        return os.path.join(self._get_games_dir_path(), game_name)

    def _delete_from_game_to_load(self, game_name: str):
        game_to_load = self.read_game_to_load()
        if game_to_load == game_name:
            game_names = self.load_game_names()
            if game_name in game_names:
                game_names.remove(game_name)
            if len(game_names) > 0:
                self._save_game_to_load(game_names[0])
            else:
                delete_file(self._get_game_to_load_file_path())
    
    def _get_game_to_load_file_path(self) -> str:
        return self.__game_to_load_file

    def _get_games_dir_path(self) -> str:
        return self.__games_dir
