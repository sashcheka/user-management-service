FROM python:3.10-slim

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN poetry install

COPY . /app
CMD ["python", "main.py"]