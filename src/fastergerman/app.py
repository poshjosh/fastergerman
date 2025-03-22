import logging
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

from fastergerman.config import LoggingConfig, AppConfig
from fastergerman.file import load_yaml
from fastergerman.i18n import I18n

logger = logging.getLogger(__name__)

class App:
    __shutting_down = False
    __shutdown = False

    __shutdown_callbacks = [Callable[[], None]]

    def __init__(self,
                 app_config_path: str = None,
                 logging_config_path: str = None):
        app_config_path = 'resources/config/app.yaml' if not app_config_path else app_config_path
        logging_config_path = 'resources/config/logging.yaml' if not logging_config_path \
            else logging_config_path
        self.config = AppConfig(load_yaml(app_config_path))
        self.logging_config = LoggingConfig(load_yaml(logging_config_path))
        paths = App._get_profile_logging_config_paths(self.config)
        for path in paths:
            self.logging_config = self.logging_config.with_updates(load_yaml(path))
        print(f"{datetime.now()} | Logging config: {self.logging_config}")
        log_file = Path(self.logging_config.get_filename())
        if log_file.exists() is False:
            log_file.parent.mkdir(parents=True, exist_ok=True)
        I18n.init(self.config.get_app_language(), self.config.get_translations_dir())

    @staticmethod
    def _get_profile_logging_config_paths(cfg: AppConfig) -> [str]:
        app_profiles = cfg.get_app_profiles()
        paths = []
        for profile in app_profiles:
            path = f"resources/config/logging.{profile}.yaml"
            if os.path.exists(path) is True:
                print(f"{datetime.now()} | Additional config for logging: {path}")
                paths.append(path)
        return paths

    def start(self):
        raise NotImplementedError("Subclasses should implement the start method")

    @staticmethod
    def add_shutdown_callback(callback: Callable[[], None]):
        App.__shutdown_callbacks.append(callback)

    @staticmethod
    def shutdown():
        if App.__shutting_down is True:
            msg = "Already shutting down..." if App.__shutdown is False else "Already shut down"
            logger.info(msg)
            return
        App.__shutting_down = True
        logger.info("Shutting down...")
        [e() for e in App.__shutdown_callbacks]
        App.__shutdown = True

    @staticmethod
    def is_shutdown() -> bool:
        return App.__shutdown

    @staticmethod
    def is_shutting_down() -> bool:
        return App.__shutting_down


def _terminate_app(signum, _):
    try:
        print(f"{datetime.now().time()} Received signal {signum}")
        App.shutdown()
    finally:
        # TODO - Find out why shutdown is not achieved without this. On the other hand,
        #  when we remove this, we OFTEN receive the following warning:
        #  UserWarning: resource_tracker: There appear to be 2 leaked semaphore objects to clean up at shutdown
        print(f"{datetime.now().time()} Exiting")
        sys.exit(1)

signal.signal(signal.SIGINT, _terminate_app)
signal.signal(signal.SIGTERM, _terminate_app)