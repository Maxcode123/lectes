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
from lectes.scanner.errors import UnmatchedTextError

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
from lectes.scanner.models import UnmatchedText

unmatched_text = []

def handler(unmatched: UnmatchedText) -> None:
  unmatched_text.append(unmatched.text)

scanner.set_unmatched_handler(handler)
```

### Debugging

The `debug` argument can be passed in order to print debug logs while scanning.

```python
scanner = Scanner(config, debug=True)
```

If the scanner has already been initialized without the debug flag, the log level
can also be set to `DEBUG` by accessing the scanner's logger.

```python
from lectes import LogLevel

scanner.logger().set_level(LogLevel.DEBUG)
```
