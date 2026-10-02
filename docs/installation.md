# Installation

lectes needs Python 3.13 or newer and has no dependencies.

## As a library

```sh
pip install lectes
```

or, in a uv project:

```sh
uv add lectes
```

Either way, the [`lectes` command](cli.md) is also installed into the
environment.

## As a command-line tool

To use the `lectes` command on its own, install it as a tool. It gets an
isolated environment and is put on your `PATH`:

```sh
uv tool install lectes
```

[uv](https://docs.astral.sh/uv/) downloads Python 3.13 for you if needed.
[pipx](https://pipx.pypa.io/) works too, provided Python 3.13 is available:

```sh
pipx install lectes
```

To run it once without installing it:

```sh
uvx lectes grammar.lectes input.txt
```

When lectes is installed in an environment, `python -m lectes` runs the same
command.
