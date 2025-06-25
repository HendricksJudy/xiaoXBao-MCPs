#!/usr/bin/env bash
set -euo pipefail

mkdir -p services/{psychology,oncology_kb,radiology,vision}
mkdir -p shared/{adapters,models,utils}
mkdir -p infra/{docker,helm}
mkdir -p tests

cat > pyproject.toml <<'PYEOF'
[tool.poetry]
name = "my_project"
version = "0.1.0"
description = ""
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "*"
uvicorn = {extras = ["standard"], version = "*"}
pydantic = "*"
httpx = "*"
tenacity = "*"
prometheus-client = "*"
tiktoken = "*"

[tool.poetry.group.dev.dependencies]
pytest = "*"
pytest-asyncio = "*"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
PYEOF

cat > .pre-commit-config.yaml <<'PCEOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
PCEOF
