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

start-doc-server:
	uv run python -m mkdocs serve

deploy-documentation:
	uv run python -m mkdocs gh-deploy --config-file mkdocs.yml

build:
	uv build

clean:
	rm -rf dist src/lectes.egg-info

publish:
	uv publish
