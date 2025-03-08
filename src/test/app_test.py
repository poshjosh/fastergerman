import unittest
from unittest import mock

from flask import Flask

from fastergerman.app import App, WebApp


class AppTestCase(unittest.TestCase):
    @staticmethod
    def test_app_smoke():
        App()

    def test_webapp_should_only_start_once(self):
        with mock.patch.object(Flask, "run"):
            app = WebApp(Flask(__name__))
            started = app.start()
            self.assertTrue(started)
            started = app.start()
            self.assertFalse(started)


if __name__ == '__main__':
    unittest.main()
