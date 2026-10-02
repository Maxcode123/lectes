<p align="center">
  <a href="https://lectes.dev">
    <img src="docs/assets/banner.png" alt="lectes: name the rules, get the tokens" width="100%">
  </a>
</p>

<p align="center">
  <a href="https://lectes.dev"><b>▶ Playground</b></a>
  &nbsp;·&nbsp;
  <a href="https://maximosnikiforakis.gr/lectes/"><b>Documentation</b></a>
  &nbsp;·&nbsp;
  <a href="https://pypi.org/project/lectes/"><b>PyPI</b></a>
</p>

# lectes

**Name the rules. Get the tokens.** lectes is a small Python scanner (lexer)
generator. Give it named regexes, and it yields tokens.

- **No dependencies.** It uses only the standard library and needs Python 3.13+.
- **Predictable matching.** The longest match wins, and a tie goes to the
  earlier rule.
- **Grammar files.** Write one `NAME  regex` rule per line, in Python or in a
  `.lectes` file.
- **A `lectes` command.** Scan files or stdin from the shell, as aligned text
  or JSON Lines.
- **Locations included.** Every token carries its offset, line and column.
- **Unmatched text is reported.** By default it raises an error, but you can
  skip it or handle it yourself.

**Try it in the playground:** [lectes.dev](https://lectes.dev) lets you write a
grammar and see the tokens as you type, right in your browser. Hover a token to
see which rules fought for it.

## Installation

As a library:

```sh
pip install lectes   # or: uv add lectes
```

As a command-line tool:

```sh
uv tool install lectes                # or: pipx install lectes
uvx lectes grammar.lectes input.txt   # run once without installing
```

## Quick start

```python
from lectes import Configuration, Scanner

config = Configuration.from_text(r"""
# Longest match wins; on a tie, the earlier rule wins.
FOR     for
IN      in
ID      [a-zA-Z_][a-zA-Z0-9_]*
INT     [0-9]+
WS      [ ]+
""")

scanner = Scanner(config)

for token in scanner.scan("for item in items format 42"):
    if token.rule.name != "WS":
        print(token.location.column, token.rule.name, repr(token.literal))
```

```text
1 FOR 'for'
5 ID 'item'
10 IN 'in'
13 ID 'items'
19 ID 'format'
26 INT '42'
```

`for` matches both `FOR` and `ID` with the same length, so the earlier rule,
`FOR`, wins. `format` is an `ID`, because the longer match always wins.

You can also build the rules in Python:

```python
from lectes import Configuration, Regex, Rule

config = Configuration(
    [
        Rule(name="FOR", regex=Regex("for")),
        Rule(name="ID", regex=Regex("[a-zA-Z_][a-zA-Z0-9_]*")),
    ]
)
```

The [usage guide](https://maximosnikiforakis.gr/lectes/usage/) covers grammar
errors and warnings, custom handlers, unmatched text and debugging.

## Command line

The `lectes` command scans a file, or stdin, with a grammar file:

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

Use `--format json` for JSON Lines output, and `--check` to validate a grammar
without scanning. The exit codes are 0 on success, 1 for unmatched text, and 2
for a usage, grammar or I/O error. See the
[command-line docs](https://maximosnikiforakis.gr/lectes/cli/) for every option.

## License

[MIT](LICENSE)
