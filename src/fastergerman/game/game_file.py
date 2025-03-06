import dataclasses
import logging
import os
from pathlib import Path
from typing import Union

from fastergerman.file import create_file, read_content, write_content, write_json, read_json, \
    delete_file, delete_dir
from fastergerman.game import Game, Score, Settings

logger = logging.getLogger(__name__)

DATA_DIR_PATH = Path.home() / ".fastergerman" / "v0.0.3" / "data"
GAME_TO_LOAD_FILE_PATH = DATA_DIR_PATH / "game-to-load.txt"
GAMES_DIR_PATH = DATA_DIR_PATH / "games"


def load_game(game_name: str or None = None) -> Game:
    logger.debug(f"Loading game: {game_name}")
    if not game_name:
        game_name = get_game_to_load()
    game_dict = read_json(_get_game_file_path(game_name))
    if not game_dict:
        return Game(game_name, Settings.of_dict({}), [], Score(0, 0))
    return Game.of_dict(game_dict)


def save_game(game: Game):
    game_name = game.name
    logger.debug(f"Saving game: '{game_name}' = {game}")
    if not game_name:
        raise ValueError("No game name provided.")
    game_dict = dataclasses.asdict(game)
    if len(game_dict) == 0:
        return False
    _save_game_to_load(game_name)
    _save_json(game_dict, _get_game_file_path(game_name))
    return True


def delete_game(game_name: str):
    logger.debug(f"Deleting game: {game_name}")
    if not game_name:
        raise ValueError("No game name provided.")
    _delete_from_game_to_load(game_name)
    delete_dir(_get_game_dir_path(game_name))


def get_game_names():
    if not os.path.exists(GAMES_DIR_PATH):
        return []
    def format_for_sorting(fname):
        return os.path.getmtime(os.path.join(GAMES_DIR_PATH, fname))
    game_names = os.listdir(GAMES_DIR_PATH)
    game_names.sort(key=format_for_sorting, reverse=True) # most recent first
    return game_names


def get_game_to_load(result_if_none: str or None = None) -> Union[str, None]:
    if not os.path.exists(GAME_TO_LOAD_FILE_PATH):
        return result_if_none
    game_to_load = read_content(GAME_TO_LOAD_FILE_PATH)
    return game_to_load if game_to_load else result_if_none


def _save_json(json, path):
    if not os.path.exists(path):
        create_file(path)
        logger.debug(f"Created: {path}")
    write_json(json, path)
    logger.debug(f"Written {json}\nto {path}")


def _get_game_file_path(game_name: str):
    return _get_game_dir_path(game_name) / "data.json"


def _get_game_dir_path(game_name: str):
    return GAMES_DIR_PATH / game_name


def _save_game_to_load(game_name: str):
    if not os.path.exists(GAME_TO_LOAD_FILE_PATH):
        create_file(GAME_TO_LOAD_FILE_PATH)
        logger.debug("Created: %s", GAME_TO_LOAD_FILE_PATH)
    write_content(game_name, GAME_TO_LOAD_FILE_PATH)
    logger.debug(f"Written {game_name} to {GAME_TO_LOAD_FILE_PATH}")


def _delete_from_game_to_load(game_name: str):
    game_to_load = get_game_to_load()
    if game_to_load == game_name:
        game_names = get_game_names()
        if game_name in game_names:
            game_names.remove(game_name)
        if len(game_names) > 0:
            _save_game_to_load(game_names[0])
        else:
            delete_file(GAME_TO_LOAD_FILE_PATH)
