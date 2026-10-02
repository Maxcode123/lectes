# Changelog

## 0.4.1 - 2026-10-02

### Added

- `lectes --help` ends with usage examples and a sample grammar file.

### Changed

- Running `lectes` with no arguments prints the help and exits 0, instead of a
  usage error.

## 0.4.0 - 2026-10-02

### Added

- A `lectes` command that scans a file or stdin with a grammar file and prints
  the tokens, aligned or as JSON Lines (`--format json`). Install it with
  `uv tool install lectes` or `pipx install lectes`, or run it with
  `python -m lectes`. Exit codes: 0 on success, 1 on unmatched text, 2 on a
  usage, grammar or I/O error.
- `Configuration.from_text` builds a configuration from grammar text, one
  `NAME  regex` rule per line with `#` comments. This is the format used by the
  lectes-web playground.
- `GrammarError`, raised by `from_text` with every error in the text as
  `(line, message)` pairs in `problems`.
- `GrammarWarning`, emitted by `from_text` for each rule that can match the
  empty string, with its `line` and `message`.

## 0.3.1 - 2026-10-02

### Fixed

- Every scanner added a handler to the shared logger when it scanned, so
  long-lived processes leaked handlers and debug messages were printed once
  per handler. Scanners no longer add any handlers.
- `debug=True` no longer turns on debug output for every other scanner in the
  process.

### Changed

- The scanner logs to the `lectes.scanner` logger instead of
  `lectes.scanner.logger`, and importing lectes adds a `NullHandler` to the
  `lectes` logger. Configure `lectes` at `DEBUG` level to get every scanner's
  events through standard logging.
- Debug messages are only built when they will be emitted, which makes
  scanning faster when debug output is off.
- Debug messages show literals and unmatched text with `repr`, so newlines and
  other special characters are visible, e.g. `unmatched: '\n'`.
- Removed `Logger.handler()` and `Logger.formatter()`. `Logger` is not exported
  from `lectes`, and `Scanner.logger().set_level(LogLevel.DEBUG)` still works.

## 0.3.0 - 2026-10-01

### Breaking changes

- Text that matches no rule now raises `UnmatchedTextError` instead of being
  printed. Pass `ignore_unmatched=True` to `Scanner` to skip it, or set a
  custom handler with `set_unmatched_handler`.
- Match handlers set with `Scanner.set_handler` now receive the matched
  `Token` instead of `(literal, rule)`.
- Unmatched handlers set with `Scanner.set_unmatched_handler` now receive an
  `UnmatchedText` instead of a `str`.
- `Token` is frozen and has a required `location` field.
- `Scanner.set_unmatched_handler` raises `ScannerConfigurationError` on a
  scanner created with `ignore_unmatched=True`.
- Removed `Scanner.set_text`, `Scanner.current_string` and
  `Scanner.lookahead_string`.
- Removed `Regex.search`, `Regex.fullmatch` and the `Match` class.

### Changed

- The scanner picks the longest match among all rules at each position;
  rules configured earlier win ties. Previously keywords followed by more
  identifier characters (`exodusx`) or numbers with a fraction (`1.5`) were
  split into several tokens.
- Contiguous unmatched text is reported as one run, including text at the end
  of the input.
- A `Scanner` can be reused, and several scans can be iterated at the same
  time.

### Added

- `Location` (offset, line and column) on every `Token` and `UnmatchedText`.
- `UnmatchedText` model.
- `ScannerError`, `ScannerConfigurationError` and `UnmatchedTextError`.
- `ignore_unmatched` argument for `Scanner`.
- `Regex.match_prefix`, which matches a regex at a given position.
- All errors, `Location` and `UnmatchedText` are exported from `lectes`.

### Fixed

- `Regex` objects compare equal only when their patterns are equal, so `Rule`
  equality and handlers for rules with the same name work correctly.
- `repr` of a `Regex` with an invalid pattern no longer raises.
