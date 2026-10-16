import hashlib
import hmac
import os
from dataclasses import dataclass
from typing import Annotated, Protocol
from uuid import UUID

import redis
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError

from pinkbombs.database import IdempotencyConflict, SubmissionRepository
from pinkbombs.submission_schemas import SubmissionRequest, public_options
from pinkbombs.submission_service import SubmissionService

API_VERSION = "1.0.0"
API_V1_PREFIX = "/api/v1"
DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000,http://localhost:5173,"
    "http://127.0.0.1:3000,http://127.0.0.1:5173"
)
DEFAULT_RATE_LIMIT = 10
DEFAULT_RATE_WINDOW_SECONDS = 60
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
MIN_SECRET_LENGTH = 32
REDIS_TIMEOUT_SECONDS = 2
REQUEST_BODY_LIMIT_BYTES = 64 * 1024


class RateLimiter(Protocol):
    def hit(self, key: str, limit: int, window_seconds: int) -> bool: ...

    def ready(self) -> None: ...


class RedisRateLimiter:
    def __init__(self, url: str):
        self.client = redis.Redis.from_url(
            url,
            socket_connect_timeout=REDIS_TIMEOUT_SECONDS,
            socket_timeout=REDIS_TIMEOUT_SECONDS,
            decode_responses=True,
        )

    def hit(self, key: str, limit: int, window_seconds: int) -> bool:
        count = self.client.eval(
            "local count = redis.call('INCR', KEYS[1]); "
            "if count == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end; "
            "return count",
            1,
            key,
            window_seconds,
        )
        return count <= limit

    def ready(self) -> None:
        self.client.ping()


@dataclass(frozen=True)
class Settings:
    cors_origins: tuple[str, ...]
    rate_limit: int
    rate_window_seconds: int
    rate_limit_secret: str
    idempotency_secret: str

    @classmethod
    def from_environment(cls) -> "Settings":
        origins = os.getenv(
            "API_CORS_ORIGINS",
            DEFAULT_CORS_ORIGINS,
        )
        return cls(
            cors_origins=tuple(
                origin.strip() for origin in origins.split(",") if origin.strip()
            ),
            rate_limit=int(os.getenv("API_RATE_LIMIT", str(DEFAULT_RATE_LIMIT))),
            rate_window_seconds=int(
                os.getenv("API_RATE_WINDOW_SECONDS", str(DEFAULT_RATE_WINDOW_SECONDS))
            ),
            rate_limit_secret=os.getenv("API_RATE_LIMIT_SECRET", ""),
            idempotency_secret=os.getenv("API_IDEMPOTENCY_SECRET", ""),
        )


class RequestSizeLimitMiddleware:
    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length and int(content_length) > self.max_bytes:
            await JSONResponse(
                {"detail": "Request body is too large"},
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )(scope, receive, send)
            return
        consumed = 0

        async def limited_receive():
            nonlocal consumed
            message = await receive()
            if message["type"] == "http.request":
                consumed += len(message.get("body", b""))
                if consumed > self.max_bytes:
                    raise RequestTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except RequestTooLarge:
            await JSONResponse(
                {"detail": "Request body is too large"},
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )(scope, receive, send)


class RequestTooLarge(Exception):
    pass


def create_app(
    repository: SubmissionRepository | None = None,
    rate_limiter: RateLimiter | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    config = settings or Settings.from_environment()
    application = FastAPI(title="Pinkometre Submission API", version=API_VERSION)
    application.state.repository = repository
    application.state.rate_limiter = rate_limiter or RedisRateLimiter(
        os.getenv("REDIS_URL", DEFAULT_REDIS_URL)
    )
    application.state.service = None
    application.add_middleware(
        RequestSizeLimitMiddleware, max_bytes=REQUEST_BODY_LIMIT_BYTES
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Idempotency-Key"],
    )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": item["loc"],
                        "msg": item["msg"],
                        "type": item["type"],
                    }
                    for item in error.errors()
                ]
            },
        )

    def get_repository() -> SubmissionRepository:
        if application.state.repository is None:
            application.state.repository = SubmissionRepository.from_environment()
        return application.state.repository

    def get_service() -> SubmissionService:
        if len(config.idempotency_secret) < MIN_SECRET_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Submission service is not configured",
            )
        if application.state.service is None:
            application.state.service = SubmissionService(
                get_repository(), config.idempotency_secret
            )
        return application.state.service

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/ready")
    def readiness() -> dict[str, str]:
        try:
            get_repository().ready()
            application.state.rate_limiter.ready()
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service is not ready",
            ) from error
        return {"status": "ready"}

    @application.get(f"{API_V1_PREFIX}/options")
    def options() -> dict:
        return public_options()

    @application.post(f"{API_V1_PREFIX}/submissions")
    def create_submission(
        submission: SubmissionRequest,
        request: Request,
        response: Response,
        idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    ) -> dict[str, int]:
        if len(config.rate_limit_secret) < MIN_SECRET_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Submission service is not configured",
            )
        client_host = request.client.host if request.client else "unknown"
        rate_key = hmac.new(
            config.rate_limit_secret.encode("utf-8"),
            client_host.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        try:
            allowed = application.state.rate_limiter.hit(
                f"pinkbombs-api:rate:{rate_key}",
                config.rate_limit,
                config.rate_window_seconds,
            )
        except RedisError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limiter is unavailable",
            ) from error
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many submissions",
            )
        try:
            result = get_service().submit(submission, idempotency_key)
        except IdempotencyConflict as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Idempotency key was used with a different submission",
            ) from error
        except SQLAlchemyError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Submission could not be stored",
            ) from error
        response.status_code = (
            status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED
        )
        return {"id": result.response_id}

    return application


app = create_app()
