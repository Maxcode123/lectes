import io
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from importlib.metadata import version
from unittest import mock
from unittest_extensions import args, TestCase

from lectes.cli import main

GRAMMAR = "INT [0-9]+\nPLUS \\+\nWS \\s+\n"


class TestCli(TestCase):
    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._directory.cleanup)
        self.previous_directory = os.getcwd()
        os.chdir(self._directory.name)
        self.addCleanup(os.chdir, self.previous_directory)

    def subject(self, *argv, stdin=b""):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        stdin = io.TextIOWrapper(io.BytesIO(stdin), encoding="utf-8")

        with (
            mock.patch("sys.stdin", stdin),
            redirect_stdout(self.stdout),
            redirect_stderr(self.stderr),
        ):
            try:
                return main(list(argv))
            except SystemExit as e:
                return e.code

    def write(self, path, content):
        mode = "wb" if isinstance(content, bytes) else "w"

        with open(path, mode, **({} if mode == "wb" else {"encoding": "utf-8"})) as f:
            f.write(content)

    def stdout_lines(self):
        return self.stdout.getvalue().splitlines()

    def stderr_lines(self):
        return self.stderr.getvalue().splitlines()


class TestCliTextOutput(TestCli):
    def setUp(self):
        super().setUp()
        self.write("g.lectes", GRAMMAR)

    @args("g.lectes", stdin=b"12 + 3")
    def test_prints_one_aligned_token_per_line(self):
        self.assertResult(0)
        self.assertSequenceEqual(
            self.stdout_lines(),
            [
                "1:1     INT   '12'",
                "1:3     WS    ' '",
                "1:4     PLUS  '+'",
                "1:5     WS    ' '",
                "1:6     INT   '3'",
            ],
        )

    @args("g.lectes", stdin=b"1\n\t2")
    def test_literals_are_shown_with_repr(self):
        self.result()
        self.assertSequenceEqual(
            self.stdout_lines(),
            ["1:1     INT   '1'", "1:2     WS    '\\n\\t'", "2:2     INT   '2'"],
        )

    @args("g.lectes", stdin=(("1 " * 6 + "\n") * 10 + "12345678").encode())
    def test_long_positions_push_columns_right(self):
        self.result()
        self.assertEqual(self.stdout_lines()[-1], "11:1    INT   '12345678'")

    @args("g.lectes", "-", stdin=b"7")
    def test_dash_reads_stdin(self):
        self.result()
        self.assertSequenceEqual(self.stdout_lines(), ["1:1     INT   '7'"])

    @args("g.lectes", "in.txt")
    def test_reads_input_file(self):
        self.write("in.txt", "42")
        self.assertResult(0)
        self.assertSequenceEqual(self.stdout_lines(), ["1:1     INT   '42'"])

    @args("g.lectes", stdin=b"")
    def test_empty_input_prints_nothing(self):
        self.assertResult(0)
        self.assertEqual(self.stdout.getvalue(), "")

    @args("g.lectes", stdin=b"1 2")
    def test_writes_nothing_to_stderr(self):
        self.result()
        self.assertEqual(self.stderr.getvalue(), "")


class TestCliJsonOutput(TestCli):
    def setUp(self):
        super().setUp()
        self.write("g.lectes", GRAMMAR + "WORD \\w+\n")

    def records(self):
        return [json.loads(line) for line in self.stdout_lines()]

    @args("g.lectes", "--format", "json", stdin=b"12\n+")
    def test_prints_one_json_record_per_token(self):
        self.assertResult(0)
        self.assertSequenceEqual(
            self.records(),
            [
                {"name": "INT", "literal": "12", "offset": 0, "line": 1, "column": 1},
                {"name": "WS", "literal": "\n", "offset": 2, "line": 1, "column": 3},
                {"name": "PLUS", "literal": "+", "offset": 3, "line": 2, "column": 1},
            ],
        )

    @args("g.lectes", "--format", "json", stdin=b"12")
    def test_record_keys_are_in_a_fixed_order(self):
        self.result()
        self.assertSequenceEqual(
            list(self.records()[0]), ["name", "literal", "offset", "line", "column"]
        )

    @args("g.lectes", "--format", "json", stdin="αβ".encode())
    def test_non_ascii_literals_are_not_escaped(self):
        self.result()
        self.assertIn('"αβ"', self.stdout.getvalue())


class TestCliUnmatched(TestCli):
    def setUp(self):
        super().setUp()
        self.write("g.lectes", GRAMMAR)

    @args("g.lectes", stdin=b"12 @ 3 $")
    def test_stops_at_first_unmatched_text(self):
        self.assertResult(1)
        self.assertSequenceEqual(
            self.stdout_lines(), ["1:1     INT   '12'", "1:3     WS    ' '"]
        )
        self.assertSequenceEqual(self.stderr_lines(), ["<stdin>:1:4: unmatched '@'"])

    @args("g.lectes", "in.txt")
    def test_names_the_input_file(self):
        self.write("in.txt", "1\n@@")
        self.assertResult(1)
        self.assertSequenceEqual(self.stderr_lines(), ["in.txt:2:1: unmatched '@@'"])

    @args("g.lectes", "--ignore-unmatched", stdin=b"12 @ 3 $")
    def test_ignore_unmatched_reports_every_run_and_continues(self):
        self.assertResult(0)
        self.assertEqual(self.stdout_lines()[-1], "1:7     WS    ' '")
        self.assertSequenceEqual(
            self.stderr_lines(),
            ["<stdin>:1:4: unmatched '@'", "<stdin>:1:8: unmatched '$'"],
        )

    @args("g.lectes", "--format", "json", stdin=b"1@")
    def test_json_mode_reports_unmatched_on_stderr(self):
        self.assertResult(1)
        self.assertEqual(len(self.stdout_lines()), 1)
        self.assertSequenceEqual(self.stderr_lines(), ["<stdin>:1:2: unmatched '@'"])


class TestCliGrammar(TestCli):
    @args("g.lectes", stdin=b"1")
    def test_errors_are_reported_with_lines(self):
        self.write("g.lectes", "9X a\nID\nINT [0-9]+")
        self.assertResult(2)
        self.assertEqual(self.stdout.getvalue(), "")
        self.assertSequenceEqual(
            self.stderr_lines(),
            [
                "g.lectes:1: error: invalid rule name '9X'",
                "g.lectes:2: error: rule 'ID' has no pattern",
            ],
        )

    @args("g.lectes", stdin=b"1")
    def test_error_without_line(self):
        self.write("g.lectes", "# nothing here\n")
        self.assertResult(2)
        self.assertSequenceEqual(
            self.stderr_lines(), ["g.lectes: error: grammar has no rules"]
        )

    @args("g.lectes", stdin=b"1")
    def test_warnings_are_reported_and_scanning_continues(self):
        self.write("g.lectes", "INT [0-9]+\nOPT x?")
        self.assertResult(0)
        self.assertSequenceEqual(self.stdout_lines(), ["1:1     INT  '1'"])
        self.assertSequenceEqual(
            self.stderr_lines(),
            [
                "g.lectes:2: warning: rule 'OPT' can match the empty string; "
                "empty matches are ignored"
            ],
        )

    @args("g.lectes", "--check", stdin=b"@@@")
    def test_check_validates_without_scanning(self):
        self.write("g.lectes", GRAMMAR)
        self.assertResult(0)
        self.assertEqual(self.stdout.getvalue(), "")
        self.assertEqual(self.stderr.getvalue(), "")

    @args("g.lectes", "--check")
    def test_check_reports_errors(self):
        self.write("g.lectes", "9X a")
        self.assertResult(2)
        self.assertSequenceEqual(
            self.stderr_lines(), ["g.lectes:1: error: invalid rule name '9X'"]
        )

    @args("g.lectes", "--check")
    def test_check_reports_warnings(self):
        self.write("g.lectes", "OPT x?")
        self.assertResult(0)
        self.assertEqual(len(self.stderr_lines()), 1)

    @args("g.lectes", stdin=b"1")
    def test_grammar_with_crlf_line_endings(self):
        self.write("g.lectes", "INT [0-9]+\r\nWS \\s+\r\n")
        self.assertResult(0)


class TestCliIO(TestCli):
    @args("missing.lectes")
    def test_missing_grammar(self):
        self.assertResult(2)
        self.assertSequenceEqual(
            self.stderr_lines(),
            ["lectes: error: cannot read 'missing.lectes': No such file or directory"],
        )

    @args("g.lectes", "missing.txt")
    def test_missing_input(self):
        self.write("g.lectes", GRAMMAR)
        self.assertResult(2)
        self.assertSequenceEqual(
            self.stderr_lines(),
            ["lectes: error: cannot read 'missing.txt': No such file or directory"],
        )

    @args("g.lectes", "in.txt")
    def test_input_that_is_not_utf8(self):
        self.write("g.lectes", GRAMMAR)
        self.write("in.txt", b"123\xff")
        self.assertResult(2)
        self.assertSequenceEqual(
            self.stderr_lines(),
            [
                "lectes: error: cannot decode 'in.txt' as utf-8: "
                "invalid start byte at byte 3"
            ],
        )

    @args("g.lectes")
    def test_grammar_that_is_not_utf8(self):
        self.write("g.lectes", b"INT \xff")
        self.assertResult(2)
        self.assertSequenceEqual(
            self.stderr_lines(),
            [
                "lectes: error: cannot decode 'g.lectes' as utf-8: "
                "invalid start byte at byte 4"
            ],
        )

    @args("g.lectes", "in.txt", "--encoding", "latin-1")
    def test_encoding_applies_to_input(self):
        self.write("g.lectes", "WORD [a-zé]+")
        self.write("in.txt", "café".encode("latin-1"))
        self.assertResult(0)
        self.assertSequenceEqual(self.stdout_lines(), ["1:1     WORD  'café'"])

    @args("g.lectes", "--encoding", "nope")
    def test_unknown_encoding(self):
        self.write("g.lectes", GRAMMAR)
        self.assertResult(2)
        self.assertSequenceEqual(
            self.stderr_lines(), ["lectes: error: unknown encoding 'nope'"]
        )

    @args("g.lectes", "in.txt")
    def test_input_keeps_crlf_line_endings(self):
        self.write("g.lectes", GRAMMAR)
        self.write("in.txt", b"1\r\n2")
        self.result()
        self.assertEqual(self.stdout_lines()[1], "1:2     WS    '\\r\\n'")


class TestCliOptions(TestCli):
    @args("--version")
    def test_version(self):
        self.assertResult(0)
        self.assertEqual(self.stdout.getvalue(), f"lectes {version('lectes')}\n")

    @args()
    def test_grammar_is_required(self):
        self.assertResult(2)
        self.assertIn("usage: lectes", self.stderr.getvalue())

    @args("g.lectes", "--format", "xml")
    def test_unknown_format(self):
        self.assertResult(2)

    @args("g.lectes", "--debug", stdin=b"1@")
    def test_debug_writes_scanner_events_to_stderr(self):
        self.write("g.lectes", GRAMMAR)
        self.result()
        self.assertSequenceEqual(
            self.stderr_lines(),
            [
                "DEBUG: rule INT matched: '1'",
                "DEBUG: unmatched: '@'",
                "<stdin>:1:2: unmatched '@'",
            ],
        )


class TestModule(TestCase):
    def subject(self):
        return subprocess.run(
            [sys.executable, "-m", "lectes", "--version"],
            capture_output=True,
            text=True,
        )

    def test_runs_as_module(self):
        completed = self.result()
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, f"lectes {version('lectes')}\n")
