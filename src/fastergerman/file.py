import json
import os
from typing import AnyStr


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_file(path):
    make_dirs(os.path.dirname(path))
    if not os.path.exists(path):
        with open(path, 'a'):
            os.utime(path, None)


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
