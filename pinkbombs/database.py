from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, delete, insert, select, text
from sqlalchemy.engine import Engine, URL


class IdempotencyConflict(Exception):
    pass


@dataclass(frozen=True)
class SubmissionResult:
    response_id: int
    replayed: bool


class SubmissionRepository:
    def __init__(self, engine: Engine, idempotency_schema: str = "pinkbombs_api"):
        self.engine = engine
        metadata = MetaData()
        self.response_table = Table(
            "reponses_pinkometre", metadata, autoload_with=engine
        )
        self.consumption_table = Table("consommations", metadata, autoload_with=engine)
        self.idempotency_table = Table(
            "idempotency_keys",
            metadata,
            schema=idempotency_schema,
            autoload_with=engine,
        )
        self._validate_schema()

    @classmethod
    def from_environment(cls) -> "SubmissionRepository":
        import os

        required = ("API_DB_USER", "API_DB_PASSWORD")
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise RuntimeError(f"Missing API database settings: {', '.join(missing)}")
        url = URL.create(
            "postgresql+psycopg2",
            username=os.environ["API_DB_USER"],
            password=os.environ["API_DB_PASSWORD"],
            host=os.getenv("API_DB_HOST", "db"),
            port=int(os.getenv("API_DB_PORT", "5432")),
            database=os.getenv("API_DB_NAME", "pinkbombs"),
        )
        engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)
        return cls(engine)

    def _validate_schema(self) -> None:
        expected_response = {
            "id",
            "email",
            "impact_initial",
            "impact_apres_engagement",
            "alternative_choisie",
            "supplement_choisi",
            "consentement_omega3",
        }
        expected_consumption = {
            "id",
            "reponses_pinkometre_fk",
            "scenario",
            "produit",
            "variante",
            "frequence",
            "occurence_par_an",
            "quantite_par_occurrence",
            "unite_fr",
            "poids_annuel_kg",
        }
        if not expected_response.issubset(self.response_table.c.keys()):
            raise RuntimeError("The response table does not match the API contract")
        if not expected_consumption.issubset(self.consumption_table.c.keys()):
            raise RuntimeError("The consumption table does not match the API contract")
        if not {"key_hash", "request_hash", "response_id", "created_at"}.issubset(
            self.idempotency_table.c.keys()
        ):
            raise RuntimeError("The idempotency table does not match the API contract")

    def ready(self) -> None:
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    def submit(
        self,
        response_values: dict[str, Any],
        consumption_values: list[dict[str, Any]],
        key_hash: str,
        request_hash: str,
    ) -> SubmissionResult:
        key_table = self.idempotency_table
        with self.engine.begin() as connection:
            connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:key_hash))"),
                {"key_hash": key_hash},
            )
            connection.execute(
                delete(key_table).where(
                    key_table.c.created_at
                    < datetime.now(timezone.utc) - timedelta(hours=24)
                )
            )
            existing = connection.execute(
                select(key_table.c.request_hash, key_table.c.response_id).where(
                    key_table.c.key_hash == key_hash
                )
            ).one_or_none()
            if existing:
                if existing.request_hash != request_hash:
                    raise IdempotencyConflict
                return SubmissionResult(existing.response_id, replayed=True)

            response_id = connection.execute(
                insert(self.response_table)
                .values(**response_values)
                .returning(self.response_table.c.id)
            ).scalar_one()
            for values in consumption_values:
                connection.execute(
                    insert(self.consumption_table).values(
                        **values,
                        reponses_pinkometre_fk=response_id,
                    )
                )
            connection.execute(
                insert(key_table).values(
                    key_hash=key_hash,
                    request_hash=request_hash,
                    response_id=response_id,
                )
            )
        return SubmissionResult(response_id, replayed=False)

    def close(self) -> None:
        self.engine.dispose()
