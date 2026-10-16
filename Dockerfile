FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install --no-cache-dir \
    "fastapi>=0.143,<0.144" \
    "uvicorn>=0.29,<0.30" \
    "SQLAlchemy>=2.0.28,<3" \
    "psycopg2-binary>=2.9.9,<3" \
    "redis>=6.4,<7" \
    "email-validator>=2.3,<3"

COPY nocodb/schema.json /app/nocodb/schema.json
COPY pinkbombs_api /app/pinkbombs_api

EXPOSE 8000

CMD ["uvicorn", "pinkbombs_api.api:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
