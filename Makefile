install:
	pkg install -y python termux-api
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv sync
.PHONY: install

format:
	uv run ruff check --fix
	uv run ruff format
.PHONY: format

run:
	@uv run python main.py $(ARGS)
.PHONY: run

transfer:
	@uv run python transfer.py $(ARGS)
.PHONY: transfer
