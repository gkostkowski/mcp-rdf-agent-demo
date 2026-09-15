FROM python:3.10-slim

ENV POETRY_NO_INTERACTION=true \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir "poetry>=2.0,<3.0"

COPY pyproject.toml poetry.lock README.md ./
COPY src ./src
RUN poetry install --only main --no-ansi

EXPOSE 8000

CMD ["library-demo-mcp"]
