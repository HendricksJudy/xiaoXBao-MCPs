# xiaoXBao MCPs

This repository provides several minimal medical copilots (MCPs) written in FastAPI.

```mermaid
graph TD
    A[API Gateway] --> B(Psychology)
    A --> C(Oncology KB)
    A --> D(Radiology)
    A --> E(Vision)
```

## Setup

```bash
poetry install
export DEEPSEEK_API_KEY=xxx
export GEMINI_API_KEY=xxx
```

## Development

Useful make targets:

- `make lint` – run black, isort and flake8
- `make test` – run pytest
- `make run` – start the API gateway

Environment variables are loaded from `DEEPSEEK_API_KEY` and `GEMINI_API_KEY`.
