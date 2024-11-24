import dataclasses
import os
from pathlib import Path
from typing import Union

from .file import create_file, read_content, write_content, write_json, read_json
from .game import Game, Score

DATA_PATH = Path.home() / ".fastergerman" / "v1" / "data"
GAME_TO_LOAD_PATH = DATA_PATH / "game-to-load.txt"
GAMES_PATH = DATA_PATH / "games"


def load_game(game_name: str or None = None) -> Game:
    if not game_name:
        game_name = get_game_to_load()
    return Game(game_name,
                [] if not game_name else read_json(_get_verb_data_path(game_name)),
                load_score(game_name))


def load_score(game_name: str or None = None) -> Score:
    if not game_name:
        game_name = get_game_to_load()
    if not game_name:
        return Score(0, 0)
    return Score.of_dict(read_json(_get_score_path(game_name)))


def save_game(game: Game):
    game_name = game.name
    if not game_name:
        raise ValueError("No game name provided.")
    _write_game_to_load(game_name)
    _save_json(game.questions, _get_verb_data_path(game_name))
    _save_json(dataclasses.asdict(game.score), _get_score_path(game_name))


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


def _get_verb_data_path(game_name: str):
    return GAMES_PATH / game_name / "verb_with_prepositions.json"


def _get_score_path(game_name: str):
    return GAMES_PATH / game_name / "score.json"


def _write_game_to_load(game_name: str):
    if not os.path.exists(GAME_TO_LOAD_PATH):
        create_file(GAME_TO_LOAD_PATH)
#        print("Created: ", GAME_TO_LOAD_PATH)
    write_content(game_name, GAME_TO_LOAD_PATH)
