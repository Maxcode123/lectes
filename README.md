# lectes

`lectes` is a simple Python scanner generator. It can be used to easily define
scanners with Python code.

**Documentation:** <https://maxcode123.github.io/lectes/>

**Example**

```python
from lectes import Rule, Configuration, Regex, Scanner


config = Configuration(
    [
        Rule(name="FOR", regex=Regex("for")),
        Rule(name="INT", regex=Regex("[0-9]+")),
        Rule(name="ID", regex=Regex("[a-zA-Z][a-zA-Z0-9]*")),
        Rule(name="WHITESPACE", regex=Regex("( )")),
    ]
)

scanner = Scanner(config)

program = "somevar in othervar for 9 let"

for token in scanner.scan(program):
    print(token)
```

## Installation

```sh
pip install lectes
```
