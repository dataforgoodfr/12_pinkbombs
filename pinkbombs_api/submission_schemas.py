import json
from decimal import Decimal
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "nocodb" / "schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
OPTIONS = SCHEMA["options"]


def validate_option(category: str, code: str | None) -> str | None:
    if code is None:
        return None
    allowed = {option.get("code") for option in OPTIONS[category]}
    if code not in allowed:
        raise ValueError(f"Unknown {category} option")
    return code


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ResponseSubmission(StrictModel):
    email: EmailStr | None = None
    impact_initial: str | None = None
    impact_apres_engagement: str | None = None
    alternative_choisie: str | None = None
    supplement_choisi: str | None = None
    consentement_omega3: bool = False

    @field_validator("impact_initial", "impact_apres_engagement")
    @classmethod
    def validate_impact(cls, value: str | None) -> str | None:
        return validate_option("impacts", value)

    @field_validator("alternative_choisie")
    @classmethod
    def validate_alternative(cls, value: str | None) -> str | None:
        return validate_option("alternatives", value)

    @field_validator("supplement_choisi")
    @classmethod
    def validate_supplement(cls, value: str | None) -> str | None:
        return validate_option("supplements", value)


NonNegativeDecimal = Annotated[
    Decimal,
    Field(ge=0, max_digits=30, decimal_places=10, allow_inf_nan=False),
]


class ConsumptionSubmission(StrictModel):
    scenario: str
    produit: str | None = None
    variante: str | None = None
    frequence: str | None = None
    occurence_par_an: NonNegativeDecimal | None = None
    quantite_par_occurrence: NonNegativeDecimal | None = None
    unite_fr: str | None = None
    poids_annuel_kg: NonNegativeDecimal | None = None

    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, value: str) -> str:
        return validate_option("scenarios", value)

    @field_validator("produit")
    @classmethod
    def validate_product(cls, value: str | None) -> str | None:
        return validate_option("produits", value)

    @field_validator("variante")
    @classmethod
    def validate_variant(cls, value: str | None) -> str | None:
        return validate_option("variantes", value)

    @field_validator("frequence")
    @classmethod
    def validate_frequency(cls, value: str | None) -> str | None:
        return validate_option("frequences", value)

    @field_validator("unite_fr")
    @classmethod
    def validate_unit(cls, value: str | None) -> str | None:
        return validate_option("unites", value)


class SubmissionRequest(StrictModel):
    response: ResponseSubmission
    consommations: list[ConsumptionSubmission] = Field(min_length=1, max_length=100)


def public_options() -> dict[str, list[dict[str, str]]]:
    return {
        category: [
            {"code": option["code"], "label": option["label"]} for option in options
        ]
        for category, options in OPTIONS.items()
    }
