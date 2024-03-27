FROM python:3.12-bookworm

ENV POETRY_HOME=/app/.poetry \
    POETRY_VIRTUALENVS_PREFER_ACTIVE_PYTHON=1
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="${PATH}:${POETRY_HOME}/bin"

WORKDIR /app

# COPY ./d4g-utils /app/d4g-utils
COPY ./pinkbombs /app/pinkbombs
COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml

RUN python -m venv ${VIRTUAL_ENV}

# Install dependencies
RUN poetry install
EXPOSE 8080

ENTRYPOINT [ "poetry", "run", "python", "-m", "pinkbombs.app" ]
