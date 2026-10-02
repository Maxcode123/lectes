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

## Command line

lectes also comes with a `lectes` command that scans a file or stdin with a
grammar file, one `NAME  regex` rule per line:

```sh
$ cat arithmetic.lectes
INT     [0-9]+
PLUS    \+
WS      \s+

$ echo '12 + 3' | lectes arithmetic.lectes
1:1     INT   '12'
1:3     WS    ' '
1:4     PLUS  '+'
1:5     WS    ' '
1:6     INT   '3'
1:7     WS    '\n'
```

Use `--format json` for JSON Lines output. See the
[command-line docs](https://maxcode123.github.io/lectes/cli/) for every option.

## Installation

As a library:

```sh
pip install lectes
```

As a command-line tool:

```sh
uv tool install lectes   # or: pipx install lectes
uvx lectes grammar.lectes input.txt   # run once without installing
```
