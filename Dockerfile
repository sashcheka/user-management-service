FROM python:3.10-alpine as builder

WORKDIR /app

RUN apk update && apk add --no-cache build-base && pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-root --with dev &&  \
    poetry export -f requirements.txt --output requirements.txt --with dev && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . /app

CMD ["python", "-m", "main.py"]
