install:
	pkg install -y python termux-api
	@command -v uv >/dev/null 2>&1 || pkg install -y uv
	uv sync --no-dev
.PHONY: install

format:
	uv run --group dev ruff check --fix
	uv run --group dev ruff format
.PHONY: format

run:
	@uv run python main.py $(ARGS)
.PHONY: run

transfer:
	@uv run python transfer.py $(ARGS)
.PHONY: transfer
