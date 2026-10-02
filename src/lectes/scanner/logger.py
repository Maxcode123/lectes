import logging
import sys
from enum import Enum

_logger = logging.getLogger("lectes.scanner")
_debug_handler: logging.Handler | None = None


class LogLevel(Enum):
    """
    Log level options for the scanner's logger.
    """

    DEBUG = "DEBUG"


class _StderrHandler(logging.StreamHandler):
    """
    Writes to whatever `sys.stderr` is when a record is emitted, rather than
    the stream at construction time, so `contextlib.redirect_stderr` works.
    """

    def __init__(self) -> None:
        logging.Handler.__init__(self)

    @property
    def stream(self):  # type: ignore[override]
        return sys.stderr


def _get_debug_handler() -> logging.Handler:
    global _debug_handler

    if _debug_handler is None:
        _debug_handler = _StderrHandler()
        _debug_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    return _debug_handler


class Logger:
    """
    Logger class for the scanner.

    Records always go to the standard `lectes.scanner` logger, so configuring
    the `lectes` logger at DEBUG level shows the events of every scanner.
    Setting this logger's level to `LogLevel.DEBUG` additionally prints its
    own scanner's events to stderr, without changing any logger's level or
    attaching any handler.
    """

    def __init__(self) -> None:
        self._debug = False

    def set_level(self, level: LogLevel) -> None:
        self._debug = level is LogLevel.DEBUG

    def enabled(self) -> bool:
        """
        Return whether a debug message would be emitted anywhere.
        """
        return self._debug or _logger.isEnabledFor(logging.DEBUG)

    def debug(self, message: str, *args: object) -> None:
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(message, *args)

        if self._debug:
            record = _logger.makeRecord(
                _logger.name, logging.DEBUG, "", 0, message, args, None
            )
            _get_debug_handler().handle(record)

    def logger(self) -> logging.Logger:
        return _logger
