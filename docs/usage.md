# Usage

## Defining the scanning rules

You have to define a set of `Rule`s based on which the scanner will operate.  
A `Rule` is just a named regex pattern.

```python
from lectes import Rule, Regex, Configuration

config = Configuration(
  [
    Rule(name="FOR", regex=Regex("for")),
    Rule(name="IN", regex=Regex("in")),
    Rule(name="ID", regex=Regex("[a-zA-Z_][a-zA-Z_0-9]*")),
    Rule(name="COLON", regex=Regex(":")),
    Rule(name="WHITESPACE", regex=Regex("( )")),
  ]
)
```

### Defining the rules in a grammar

The same rules can be written as grammar text, one rule per line: a name,
whitespace, then the regex, which is the rest of the line. Blank lines and
lines starting with `#` are ignored. This is the format the
[`lectes` command](cli.md) reads.

```python
from lectes import Configuration

config = Configuration.from_text(
  r"""
  # a tiny language
  FOR         for
  IN          in
  ID          [a-zA-Z_][a-zA-Z_0-9]*
  COLON       :
  WHITESPACE  ( )
  """
)
```

Use a raw string, or read the grammar from a file, so that backslashes in the
regexes reach the parser unchanged.

If the text has errors, `from_text` raises a `GrammarError`. Its `problems`
list holds every error found, as `(line, message)` pairs, so all of them can be
fixed at once. `line` is `None` for problems that aren't tied to a line, such as
an empty grammar.

```python
from lectes import GrammarError

try:
  Configuration.from_text("9X a\nID")
except GrammarError as e:
  print(e.problems)  # [(1, "invalid rule name '9X'"), (2, "rule 'ID' has no pattern")]
```

Rules that are valid but probably not what was intended, such as one that can
match the empty string, emit a `GrammarWarning` through the `warnings` module.
Each warning carries its `line` and `message`.

```python
import warnings
from lectes import GrammarWarning

with warnings.catch_warnings(record=True) as caught:
  warnings.simplefilter("always", GrammarWarning)
  config = Configuration.from_text("OPT x?")

for warning in caught:
  print(warning.message.line, warning.message.message)
```

## Scanning

The scanner only requires a `Configuration` of `Rule`s to be initialized, it
 can then scan any given text based on that configuration.

```python
from lectes import Rule, Regex, Configuration, Scanner

config = Configuration(
  [
    Rule(name="FOR", regex=Regex("for")),
    Rule(name="IN", regex=Regex("in")),
    Rule(name="ID", regex=Regex("[a-zA-Z_][a-zA-Z_0-9]*")),
    Rule(name="COLON", regex=Regex(":")),
    Rule(name="WHITESPACE", regex=Regex("( )")),
  ]
)

scanner = Scanner(config)

for token in scanner.scan("for var in array:"):
  print(token)
```

### Defining custom handlers

When a rule is matched, the default behaviour of the scanner is to yield a
`Token` object. A token holds the matched `rule`, the matched `literal` and the
`location` where the literal starts in the text (its `offset`, `line` and
`column`).

This behaviour can be tweaked by defining custom handlers for individual rules.
A handler receives the matched `Token`; whatever it returns is yielded by the
scanner, unless it returns `None`, in which case the token is skipped.

```python
from lectes import Rule, Regex, Configuration, Scanner, Token

config = Configuration(
  [
    Rule(name="FOR", regex=Regex("for")),
    Rule(name="IN", regex=Regex("in")),
    Rule(name="ID", regex=Regex("[a-zA-Z_][a-zA-Z_0-9]*")),
    Rule(name="COLON", regex=Regex(":")),
    Rule(name="WHITESPACE", regex=Regex("( )")),
  ]
)

def whitespace_handler(token: Token) -> None:
  return

ids = []

def id_handler(token: Token) -> Token:
  ids.append(token.literal)
  return token

# You don't have to return a Token
def for_handler(token: Token) -> dict:
  return {"matched": token.literal, "line": token.location.line}

scanner = Scanner(config)
scanner.set_handler(config.rules[0], for_handler)
scanner.set_handler(config.rules[2], id_handler)
scanner.set_handler(config.rules[4], whitespace_handler)

for token in scanner.scan("for var in array:"):
  print(token)

print(ids)
```

### Handling unmatched text

By default, the scanner raises an `UnmatchedTextError` when part of the text
does not match any rule. Each contiguous run of unmatched text is reported
once, together with the location where it starts. Since `scan` is a generator,
the tokens before the unmatched text have already been yielded when the error
is raised.

```python
from lectes import UnmatchedTextError

try:
  tokens = list(scanner.scan("for var in array?"))
except UnmatchedTextError as e:
  print(e)  # unmatched text '?' at line 1, column 17
  print(e.unmatched.text, e.unmatched.location.line, e.unmatched.location.column)
```

To skip unmatched text instead, create the scanner with `ignore_unmatched=True`.

```python
scanner = Scanner(config, ignore_unmatched=True)
```

To handle unmatched text yourself, define a custom handler. It receives an
`UnmatchedText` with the `text` and its `location`, and replaces the default
behaviour of raising an error. A custom handler cannot be combined with
`ignore_unmatched=True`; trying to set one raises a `ScannerConfigurationError`.

```python
from lectes import UnmatchedText

unmatched_text = []

def handler(unmatched: UnmatchedText) -> None:
  unmatched_text.append(unmatched.text)

scanner.set_unmatched_handler(handler)
```

### Debugging

The `debug` argument can be passed in order to print the scanner's matches and
unmatched text to stderr while scanning.

```python
scanner = Scanner(config, debug=True)
```

```
DEBUG: rule ID matched: 'somevar'
DEBUG: unmatched: '@'
```

Only this scanner's events are printed; other scanners are not affected.

If the scanner has already been initialized without the debug flag, debug output
can also be turned on by accessing the scanner's logger.

```python
from lectes import LogLevel

scanner.logger().set_level(LogLevel.DEBUG)
```

#### Using standard logging

lectes logs through the standard `logging` module, under the `lectes` logger.
To send the events of every scanner to your application's logging setup,
configure that logger at `DEBUG` level instead of passing `debug=True`.

```python
import logging

logging.basicConfig(format="%(name)s: %(message)s")
logging.getLogger("lectes").setLevel(logging.DEBUG)
```
