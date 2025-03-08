import os
import unittest
from pathlib import Path

from fastergerman.config import AppConfig


class ConfigTestCase(unittest.TestCase):
    def _should_expand_path(self, value, expected):
        data = { "app": { "dir": value, "name":"test", "version":"1" } }
        config = AppConfig(data)
        if "APP_DIR" in os.environ:
            del os.environ["APP_DIR"]
        self.assertEqual(expected, config.get_app_dir())

    def test_path_expansion(self):
        expected = os.path.join(Path.home(), "dir")
        values = ["~/dir", "$HOME/dir", "${HOME}/dir"]
        for value in values:
            self._should_expand_path(value, expected)


if __name__ == '__main__':
    unittest.main()
