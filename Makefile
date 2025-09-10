lint:
	ruff check --exclude src/lectes/tests

format:
	ruff format ./

type-check:
	uv run ty check

install-local-package:
	uv pip install -e .

test:
	uv run python -m unittest discover -v src/lectes/tests/unit
