import hashlib
import hmac
import json
from uuid import UUID

from pinkbombs_api.database import SubmissionRepository, SubmissionResult
from pinkbombs_api.submission_schemas import OPTIONS, SubmissionRequest


class SubmissionService:
    def __init__(self, repository: SubmissionRepository, idempotency_secret: str):
        if len(idempotency_secret) < 32:
            raise ValueError(
                "API_IDEMPOTENCY_SECRET must contain at least 32 characters"
            )
        self.repository = repository
        self.secret = idempotency_secret.encode("utf-8")

    def submit(
        self, submission: SubmissionRequest, idempotency_key: UUID
    ) -> SubmissionResult:
        payload = submission.model_dump(mode="json", exclude_none=True)
        canonical_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        key_hash = self._digest(f"key:{idempotency_key}")
        request_hash = self._digest(f"payload:{canonical_payload}")
        response_values = {
            field: self._label(category, code)
            for field, category, code in (
                ("impact_initial", "impacts", submission.response.impact_initial),
                (
                    "impact_apres_engagement",
                    "impacts",
                    submission.response.impact_apres_engagement,
                ),
                (
                    "alternative_choisie",
                    "alternatives",
                    submission.response.alternative_choisie,
                ),
                (
                    "supplement_choisi",
                    "supplements",
                    submission.response.supplement_choisi,
                ),
            )
            if code is not None
        }
        response_values["consentement_omega3"] = submission.response.consentement_omega3
        if submission.response.email is not None:
            response_values["email"] = str(submission.response.email)

        consumption_values = []
        for consumption in submission.consommations:
            values = consumption.model_dump(exclude_none=True)
            for field, category in (
                ("scenario", "scenarios"),
                ("produit", "produits"),
                ("variante", "variantes"),
                ("frequence", "frequences"),
                ("unite_fr", "unites"),
            ):
                if field in values:
                    values[field] = self._label(category, values[field])
            consumption_values.append(values)

        return self.repository.submit(
            response_values,
            consumption_values,
            key_hash,
            request_hash,
        )

    def _digest(self, value: str) -> str:
        return hmac.new(self.secret, value.encode("utf-8"), hashlib.sha256).hexdigest()

    @staticmethod
    def _label(category: str, code: str) -> str:
        for option in OPTIONS[category]:
            if option.get("code") == code:
                return option["label"]
        raise ValueError(f"Unknown option in {category}")
