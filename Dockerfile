FROM python:3.10-alpine as builder

WORKDIR /app

RUN apk update && apk add --no-cache build-base libffi-dev openssl-dev

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN poetry install --no-dev

FROM python:3.10-alpine

WORKDIR /app

COPY --from=builder /usr/local /usr/local

COPY . /app

CMD ["python", "main.py"]
