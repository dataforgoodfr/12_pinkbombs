from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from pinkbombs import api, verify_token
from pinkbombs.auth.cors import origins

app = FastAPI()
GRAPHS = ["aqua-tonnes"]
TOKEN = "pinkbombs"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api/v1/secure", dependencies=[Depends(verify_token)])
