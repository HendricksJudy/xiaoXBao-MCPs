FROM python:3.11-slim
ENV POETRY_VERSION=1.8.2
COPY pyproject.toml .
RUN pip install poetry==$POETRY_VERSION && poetry install --no-dev
COPY . /app
WORKDIR /app
CMD ["uvicorn","services.psychology.main:app","--host","0.0.0.0","--port","8080"]
