import dataclasses
import os
from pathlib import Path
from typing import Union

from .file import create_file, read_content, write_content, write_json, read_json
from .game import Game, Score, Settings

DATA_PATH = Path.home() / ".fastergerman" / "v0.0.2" / "data"
GAME_TO_LOAD_PATH = DATA_PATH / "game-to-load.txt"
GAMES_PATH = DATA_PATH / "games"


def load_game(game_name: str or None = None) -> Game:
    if not game_name:
        game_name = get_game_to_load()
    game_dict = read_json(_get_game_path(game_name))
    if not game_dict:
        return Game(game_name, Settings.of_dict({}), [], Score(0, 0))
    return Game.of_dict(game_dict)


def save_game(game: Game):
    game_name = game.name
    if not game_name:
        raise ValueError("No game name provided.")
    _save_game_to_load(game_name)
    _save_json(dataclasses.asdict(game), _get_game_path(game_name))


def get_game_names():
    if not os.path.exists(GAMES_PATH):
        return []
    return os.listdir(GAMES_PATH)


def get_game_to_load(result_if_none: str or None = None) -> Union[str, None]:
    if not os.path.exists(GAME_TO_LOAD_PATH):
        return result_if_none
    game_to_load = read_content(GAME_TO_LOAD_PATH)
    return game_to_load if game_to_load else result_if_none


def _save_json(json, path):
    if not os.path.exists(path):
        create_file(path)
        # print("Created: ", path)
    write_json(json, path)


def _get_game_path(game_name: str):
    return GAMES_PATH / game_name / "data.json"


def _save_game_to_load(game_name: str):
    if not os.path.exists(GAME_TO_LOAD_PATH):
        create_file(GAME_TO_LOAD_PATH)
#        print("Created: ", GAME_TO_LOAD_PATH)
    write_content(game_name, GAME_TO_LOAD_PATH)
