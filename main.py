from fastapi import FastAPI, Depends
from pinkbombs import api, verify_token

GRAPHS = ["aqua-tonnes"]
TOKEN = "pinkbombs"

app = FastAPI()

app.include_router(
    api.router,
    prefix="/api/v1/secure",
    dependencies=[Depends(verify_token)]
)