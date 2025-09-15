import logging
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"


class Logger:
    def __init__(self) -> None:
        self._logger = None
        self._handler = None
        self._formatter = None

    def set_level(self, level: LogLevel) -> None:
        self.logger().setLevel(self._map_level(level))
        self.handler().setLevel(self._map_level(level))

    def debug(self, message: str) -> None:
        self.logger().debug(message)

    def logger(self) -> logging.Logger:
        if self._logger is None:
            self._logger = self._build_logger()

        return self._logger

    def handler(self) -> logging.StreamHandler:
        if self._handler is None:
            self._handler = self._build_handler()

        return self._handler

    def formatter(self) -> logging.Formatter:
        if self._formatter is None:
            self._formatter = self._build_formatter()

        return self._formatter

    def _build_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.addHandler(self.handler())

        return logger

    def _build_handler(self) -> logging.StreamHandler:
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter())

        return handler

    def _build_formatter(self) -> logging.Formatter:
        return logging.Formatter("%(levelname)s: %(message)s")

    def _map_level(self, level: LogLevel) -> int:
        match level:
            case LogLevel.DEBUG:
                return logging.DEBUG
            case _:
                return logging.INFO
