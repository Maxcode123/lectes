lint:
	ruff check

format:
	ruff format ./

type-check:
	uv run ty check

install-local-package:
	uv pip install -e .
