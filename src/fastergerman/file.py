import json
import logging
import os
import shutil
import yaml
from typing import AnyStr, Any

logger = logging.getLogger(__name__)


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_file(path):
    make_dirs(os.path.dirname(path))
    if not os.path.exists(path):
        with open(path, 'a'):
            os.utime(path, None)


def delete_file(path):
    if not os.path.isfile(path):
        raise ValueError(f"Not a file: {path}")
    if os.path.exists(path):
        os.remove(path)
        return True
    else:
        return False


def delete_dir(path):
    if not os.path.isdir(path):
        raise ValueError(f"Not a directory: {path}")
    if os.path.exists(path):
        shutil.rmtree(path)
        return True
    else:
        return False


def read_content(file_path):
    with open(file_path, 'r+') as text_file:
        return text_file.read()


def read_json(file_path):
    with open(file_path, 'r+') as openfile:
        return json.load(openfile)


def write_content(content: AnyStr, file_path):
    with open(file_path, 'w+') as text_file:
        text_file.write(content)


def write_json(python_obj, file_path):
    with open(file_path, 'w+') as outfile:
        json.dump(python_obj, outfile)


def load_yaml(yaml_file_path: str, file_open_mode='r') -> Any:
    logger.debug(f'Will load yaml from: {yaml_file_path}')
    with open(yaml_file_path, file_open_mode) as yaml_file:
        config = yaml.full_load(yaml_file)
        logger.debug(f'Loaded yaml: {config}')
        return config


def load_yaml_str(yaml_str: str) -> Any:
    config = yaml.full_load(yaml_str)
    logger.debug(f'Loaded yaml: {config}')
    return config


def save_yaml(obj: Any, yaml_file_path: str, file_open_mode='w') -> Any:
    logger.debug(f'Will save yaml to: {yaml_file_path}')
    with open(yaml_file_path, file_open_mode) as yaml_file:
        config = yaml.dump(obj, yaml_file)
        logger.debug(f'Saved yaml: {config}')
        return config
