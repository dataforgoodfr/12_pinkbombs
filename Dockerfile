FROM python:3.12-bookworm

ARG API_KEY=pinkbombs
ENV PINKBOMBS_API_KEY=$API_KEY

ENV POETRY_HOME=/app/.poetry \
    POETRY_VIRTUALENVS_PREFER_ACTIVE_PYTHON=1
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="${PATH}:${POETRY_HOME}/bin"

RUN apt-get update && apt-get install --yes libgdal-dev

WORKDIR /app

# COPY ./d4g-utils /app/d4g-utils
COPY ./pinkbombs ./pinkbombs
COPY ./data ./data
COPY main.py ./main.py
COPY poetry.lock ./poetry.lock
COPY pyproject.toml ./pyproject.toml

RUN python -m venv ${VIRTUAL_ENV}

# Install dependencies
RUN poetry install

EXPOSE 8080
ENTRYPOINT [ "poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
