"""
The `lectes` command: scan a file or stdin with a grammar file.
"""

import argparse
import codecs
import json
import os
import sys
import warnings
from importlib.metadata import PackageNotFoundError, version
from typing import Callable

from lectes.config.errors import GrammarError, GrammarWarning
from lectes.config.models import Configuration
from lectes.scanner.errors import UnmatchedTextError
from lectes.scanner.models import Token, UnmatchedText
from lectes.scanner.scanner import Scanner

_STDIN = "-"
_POSITION_WIDTH = 8


class _InputError(Exception):
    """
    A file can't be read or decoded; the message is ready to print.
    """


def main(argv: list[str] | None = None) -> int:
    """
    Run the command with the given arguments and return its exit code: 0 on
    success, 1 on unmatched text and 2 on a usage, grammar or I/O error.

    With no arguments at all, print the help, as `--help` does.
    """
    parser = _parser()

    if not (sys.argv[1:] if argv is None else argv):
        parser.print_help()
        return 0

    arguments = parser.parse_args(argv)

    try:
        codecs.lookup(arguments.encoding)
    except LookupError:
        return _fail(f"unknown encoding {arguments.encoding!r}")

    try:
        grammar = _read(arguments.grammar, "utf-8")
    except _InputError as e:
        return _fail(str(e))

    configuration = _configuration(arguments.grammar, grammar)

    if configuration is None:
        return 2

    if arguments.check:
        return 0

    try:
        text = _read(arguments.input, arguments.encoding)
    except _InputError as e:
        return _fail(str(e))

    try:
        return _scan(configuration, text, arguments)
    except BrokenPipeError:
        # The reader went away (e.g. `| head`); stop quietly.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lectes",
        description="Scan a file or stdin with a lectes grammar and print the tokens.",
    )
    parser.add_argument("grammar", help="grammar file, one 'NAME  regex' rule per line")
    parser.add_argument(
        "input",
        nargs="?",
        default=_STDIN,
        help="file to scan; reads stdin when omitted or '-'",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="'text' for aligned lines, 'json' for one JSON object per line",
    )
    parser.add_argument(
        "--ignore-unmatched",
        action="store_true",
        help="report unmatched text on stderr and keep scanning, exiting 0",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="encoding of the input (default: utf-8); the grammar is always utf-8",
    )
    parser.add_argument(
        "--check", action="store_true", help="only validate the grammar"
    )
    parser.add_argument(
        "--debug", action="store_true", help="print scanner debug events to stderr"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_version()}")

    return parser


def _version() -> str:
    try:
        return version("lectes")
    except PackageNotFoundError:
        return "unknown"


def _read(path: str, encoding: str) -> str:
    name = _display_name(path)

    try:
        if path == _STDIN:
            data = sys.stdin.buffer.read()
        else:
            with open(path, "rb") as f:
                data = f.read()
    except OSError as e:
        raise _InputError(f"cannot read {name!r}: {e.strerror}") from None

    try:
        return data.decode(encoding)
    except UnicodeDecodeError as e:
        raise _InputError(
            f"cannot decode {name!r} as {encoding}: {e.reason} at byte {e.start}"
        ) from None


def _configuration(path: str, grammar: str) -> Configuration | None:
    name = _display_name(path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", GrammarWarning)

        try:
            configuration = Configuration.from_text(grammar)
        except GrammarError as e:
            for line, message in e.problems:
                _report(name, line, f"error: {message}")

            return None

    for warning in caught:
        if isinstance(warning.message, GrammarWarning):
            _report(name, warning.message.line, f"warning: {warning.message}")
        else:
            warnings.warn_explicit(
                warning.message, warning.category, warning.filename, warning.lineno
            )

    return configuration


def _scan(
    configuration: Configuration, text: str, arguments: argparse.Namespace
) -> int:
    name = _display_name(arguments.input)
    scanner = Scanner(configuration, debug=arguments.debug)
    write = (
        _json_writer() if arguments.format == "json" else _text_writer(configuration)
    )

    def report(unmatched: UnmatchedText) -> None:
        location = unmatched.location
        _report(
            name, f"{location.line}:{location.column}", f"unmatched {unmatched.text!r}"
        )

    if arguments.ignore_unmatched:
        scanner.set_unmatched_handler(report)

    try:
        for token in scanner.scan(text):
            write(token)
    except UnmatchedTextError as e:
        sys.stdout.flush()
        report(e.unmatched)
        return 1

    sys.stdout.flush()
    return 0


def _text_writer(configuration: Configuration) -> Callable[[Token], None]:
    width = max(len(rule.name) for rule in configuration.rules)

    def write(token: Token) -> None:
        location = token.location
        position = f"{location.line}:{location.column}"
        sys.stdout.write(
            f"{position:<{_POSITION_WIDTH}}{token.name:<{width}}  {token.literal!r}\n"
        )

    return write


def _json_writer() -> Callable[[Token], None]:
    def write(token: Token) -> None:
        location = token.location
        record = {
            "name": token.name,
            "literal": token.literal,
            "offset": location.offset,
            "line": location.line,
            "column": location.column,
        }
        sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")

    return write


def _display_name(path: str) -> str:
    return "<stdin>" if path == _STDIN else path


def _report(name: str, position: int | str | None, message: str) -> None:
    prefix = name if position is None else f"{name}:{position}"
    print(f"{prefix}: {message}", file=sys.stderr)


def _fail(message: str) -> int:
    print(f"lectes: error: {message}", file=sys.stderr)
    return 2
