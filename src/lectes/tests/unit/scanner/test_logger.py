import io
import logging
from contextlib import redirect_stderr, redirect_stdout
from unittest_extensions import args, TestCase

import lectes
from lectes.config.models import Rule, Configuration
from lectes.engine.models import Regex
from lectes.scanner.logger import LogLevel
from lectes.scanner.scanner import Scanner


def configuration():
    return Configuration([Rule(name="A", regex=Regex("a"))])


def handler_counts():
    loggers = [logging.getLogger()] + [
        logger
        for logger in logging.root.manager.loggerDict.values()
        if isinstance(logger, logging.Logger)
    ]
    return {logger.name: len(logger.handlers) for logger in loggers}


class TestPackageLogger(TestCase):
    def test_lectes_logger_has_one_null_handler(self):
        handlers = logging.getLogger(lectes.__name__).handlers

        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], logging.NullHandler)


class ScannerLoggingTestCase(TestCase):
    def subject(self, text, debug):
        self.stderr = io.StringIO()
        self.stdout = io.StringIO()

        with redirect_stderr(self.stderr), redirect_stdout(self.stdout):
            for scanner in self.scanners(debug):
                list(scanner.scan(text))

    def scanners(self, debug):
        return [Scanner(configuration(), debug=debug, ignore_unmatched=True)]

    def stderr_lines(self):
        return self.stderr.getvalue().splitlines()


class TestScannerLogging(ScannerLoggingTestCase):
    @args("ab", debug=True)
    def test_debug_writes_one_line_per_event(self):
        self.result()
        self.assertSequenceEqual(
            self.stderr_lines(), ["DEBUG: rule A matched: 'a'", "DEBUG: unmatched: 'b'"]
        )

    @args("a\n", debug=True)
    def test_debug_shows_literals_with_repr(self):
        self.result()
        self.assertSequenceEqual(
            self.stderr_lines(),
            ["DEBUG: rule A matched: 'a'", "DEBUG: unmatched: '\\n'"],
        )

    @args("ab", debug=False)
    def test_no_debug_writes_nothing(self):
        self.result()
        self.assertEqual(self.stderr.getvalue(), "")

    @args("ab", debug=True)
    def test_nothing_is_written_to_stdout(self):
        self.result()
        self.assertEqual(self.stdout.getvalue(), "")

    @args("ab", debug=True)
    def test_debug_does_not_change_logger_levels(self):
        levels = [logging.getLogger(n).level for n in ("lectes", "lectes.scanner")]
        self.result()
        self.assertSequenceEqual(
            [logging.getLogger(n).level for n in ("lectes", "lectes.scanner")], levels
        )


class TestScannerLoggingWithOtherScanner(ScannerLoggingTestCase):
    def scanners(self, debug):
        return [
            Scanner(configuration(), debug=debug, ignore_unmatched=True),
            Scanner(configuration(), ignore_unmatched=True),
        ]

    @args("ab", debug=True)
    def test_other_scanner_writes_nothing(self):
        self.result()
        self.assertSequenceEqual(
            self.stderr_lines(), ["DEBUG: rule A matched: 'a'", "DEBUG: unmatched: 'b'"]
        )


class TestScannerLoggingSetLevel(ScannerLoggingTestCase):
    def scanners(self, debug):
        scanner = Scanner(configuration(), ignore_unmatched=True)
        scanner.logger().set_level(LogLevel.DEBUG)
        return [scanner]

    @args("ab", debug=None)
    def test_set_level_enables_debug(self):
        self.result()
        self.assertSequenceEqual(
            self.stderr_lines(), ["DEBUG: rule A matched: 'a'", "DEBUG: unmatched: 'b'"]
        )


class TestScannerHandlers(TestCase):
    def subject(self, debug):
        with redirect_stderr(io.StringIO()):
            for _ in range(50):
                list(Scanner(configuration(), debug=debug).scan("aaa"))

    @args(debug=False)
    def test_scanning_adds_no_handlers(self):
        counts = handler_counts()
        self.result()
        self.assertEqual(handler_counts(), counts)

    @args(debug=True)
    def test_debug_scanning_adds_no_handlers(self):
        counts = handler_counts()
        self.result()
        self.assertEqual(handler_counts(), counts)


class TestStandardLogging(TestCase):
    def subject(self, text):
        with self.assertLogs("lectes", level="DEBUG") as logs:
            list(Scanner(configuration(), ignore_unmatched=True).scan(text))

        return logs

    @args("ab")
    def test_records_reach_lectes_logger(self):
        logs = self.result()
        self.assertSequenceEqual(
            logs.output,
            [
                "DEBUG:lectes.scanner:rule A matched: 'a'",
                "DEBUG:lectes.scanner:unmatched: 'b'",
            ],
        )


class _Name(str):
    """
    A rule name that records every attempt to format it.
    """

    formatted = 0

    def __str__(self):
        _Name.formatted += 1
        return super().__str__()

    def __repr__(self):
        _Name.formatted += 1
        return super().__repr__()

    def __format__(self, spec):
        _Name.formatted += 1
        return super().__format__(spec)


class TestLazyFormatting(TestCase):
    def subject(self, text):
        _Name.formatted = 0
        config = Configuration([Rule(name=_Name("A"), regex=Regex("a"))])
        list(Scanner(config).scan(text))

        return _Name.formatted

    @args("aaa")
    def test_no_formatting_without_debug(self):
        self.assertResult(0)
