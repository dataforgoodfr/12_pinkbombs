from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from pinkbombs.api import Settings, create_app
from pinkbombs.database import IdempotencyConflict, SubmissionResult
from pinkbombs.submission_schemas import public_options


class FakeRepository:
    def __init__(self):
        self.submissions = {}
        self.response_values = None
        self.consumption_values = None

    def ready(self):
        return None

    def submit(self, response_values, consumption_values, key_hash, request_hash):
        existing = self.submissions.get(key_hash)
        if existing:
            if existing[0] != request_hash:
                raise IdempotencyConflict
            return SubmissionResult(existing[1], replayed=True)
        response_id = len(self.submissions) + 1
        self.submissions[key_hash] = (request_hash, response_id)
        self.response_values = response_values
        self.consumption_values = consumption_values
        return SubmissionResult(response_id, replayed=False)


class FakeRateLimiter:
    def __init__(self, allowed=True):
        self.allowed = allowed
        self.keys = []

    def hit(self, key, limit, window_seconds):
        self.keys.append(key)
        return self.allowed

    def ready(self):
        return None


def make_client(repository=None, limiter=None):
    settings = Settings(
        cors_origins=("https://frontend.example",),
        rate_limit=10,
        rate_window_seconds=60,
        rate_limit_secret="rate-limit-secret-that-is-long-enough",
        idempotency_secret="idempotency-secret-that-is-long-enough",
    )
    repository = repository or FakeRepository()
    limiter = limiter or FakeRateLimiter()
    return TestClient(create_app(repository, limiter, settings)), repository, limiter


def valid_payload():
    return {
        "response": {
            "email": "survey@example.org",
            "impact_initial": "low",
            "consentement_omega3": True,
        },
        "consommations": [
            {
                "scenario": "initial",
                "produit": "sushi",
                "frequence": "otherYearly",
                "occurence_par_an": 17.125,
                "quantite_par_occurrence": 1.5,
                "unite_fr": "piece",
                "poids_annuel_kg": 0.1284375,
            }
        ],
    }


def post(client, payload, key=None):
    return client.post(
        "/api/v1/submissions",
        json=payload,
        headers={"Idempotency-Key": key or str(uuid4())},
    )


def test_options_expose_codes_and_french_labels():
    client, _, _ = make_client()

    response = client.get("/api/v1/options")

    assert response.status_code == 200
    assert response.json() == public_options()
    assert {"code": "null", "label": "Je ne consomme pas de saumon"} in response.json()[
        "produits"
    ]
    assert response.json()["scenarios"] == [
        {"code": "initial", "label": "Initiale"},
        {"code": "afterCommitment", "label": "Après engagement"},
    ]


def test_submission_maps_codes_and_returns_generated_id():
    client, repository, limiter = make_client()

    response = post(client, valid_payload())

    assert response.status_code == 201
    assert response.json() == {"id": 1}
    assert repository.response_values == {
        "impact_initial": "Léger",
        "consentement_omega3": True,
        "email": "survey@example.org",
    }
    assert repository.consumption_values == [
        {
            "scenario": "Initiale",
            "produit": "Sushis (makis, nigiris, sashimis)",
            "frequence": "Fréquence personnalisée, par an",
            "occurence_par_an": Decimal("17.125"),
            "quantite_par_occurrence": Decimal("1.5"),
            "unite_fr": "Pièce",
            "poids_annuel_kg": Decimal("0.1284375"),
        }
    ]
    assert limiter.keys[0].startswith("pinkbombs-api:rate:")
    assert "survey@example.org" not in limiter.keys[0]


def test_no_salmon_product_code_is_stored_as_its_french_label():
    client, repository, _ = make_client()
    payload = valid_payload()
    payload["consommations"][0]["produit"] = "null"

    response = post(client, payload)

    assert response.status_code == 201
    assert repository.consumption_values[0]["produit"] == "Je ne consomme pas de saumon"


def test_idempotent_retry_returns_same_id_and_conflicting_payload_is_rejected():
    client, _, _ = make_client()
    key = str(uuid4())
    payload = valid_payload()

    first = post(client, payload, key)
    retry = post(client, payload, key)
    changed = valid_payload()
    changed["response"]["consentement_omega3"] = False
    conflict = post(client, changed, key)

    assert first.status_code == 201
    assert retry.status_code == 200
    assert retry.json() == first.json()
    assert conflict.status_code == 409


def test_invalid_options_extra_fields_and_empty_consumptions_are_rejected():
    client, repository, _ = make_client()

    invalid_option = valid_payload()
    invalid_option["consommations"][0]["scenario"] = "not-a-scenario"
    extra_field = valid_payload()
    extra_field["response"]["id"] = 12
    no_consumptions = valid_payload()
    no_consumptions["consommations"] = []

    assert post(client, invalid_option).status_code == 422
    assert post(client, extra_field).status_code == 422
    assert post(client, no_consumptions).status_code == 422
    assert repository.submissions == {}


def test_invalid_email_and_decimal_precision_are_rejected():
    client, _, _ = make_client()
    bad_email = valid_payload()
    bad_email["response"]["email"] = "not-an-email"
    too_precise = valid_payload()
    too_precise["consommations"][0]["occurence_par_an"] = 0.12345678901

    assert post(client, bad_email).status_code == 422
    assert post(client, too_precise).status_code == 422


def test_rate_limit_rejection_does_not_write_submission():
    repository = FakeRepository()
    client, _, _ = make_client(repository, FakeRateLimiter(allowed=False))

    response = post(client, valid_payload())

    assert response.status_code == 429
    assert repository.submissions == {}


def test_health_and_readiness_routes():
    client, _, _ = make_client()

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_cors_allows_only_configured_origin():
    client, _, _ = make_client()

    allowed = client.options(
        "/api/v1/submissions",
        headers={
            "Origin": "https://frontend.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Idempotency-Key,Content-Type",
        },
    )
    denied = client.options(
        "/api/v1/submissions",
        headers={
            "Origin": "https://unknown.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.headers["access-control-allow-origin"] == "https://frontend.example"
    assert "access-control-allow-origin" not in denied.headers
