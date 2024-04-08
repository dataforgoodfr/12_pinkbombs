from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os

api_key_header = APIKeyHeader(name="X-API-Key")

TOKEN = os.environ.get("PINKBOMBS_API_KEY", "pinkbombs")

def verify_token(api_key_header: str = Security(api_key_header)):
    if api_key_header == TOKEN:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key"
    )
