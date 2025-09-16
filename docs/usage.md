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

### Handling unmatched text

The default behaviour of the scanner is to print the text that does not match
any rule. The default behaviour can be changed by defining a custom handler for
unmatched text.

```python
unmatched_text = []

def handler(unmatched: str) -> None:
  unmatched_text.append(unmatched)

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
