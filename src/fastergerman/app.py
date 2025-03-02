import logging
import signal
import sys
from datetime import datetime
from typing import Callable

logger = logging.getLogger(__name__)

class App:
    __shutting_down = False
    __shutdown = False

    __shutdown_callbacks = [Callable[[], None]]

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
