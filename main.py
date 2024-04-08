from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyQuery, APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import pandas as pd

import pinkbombs as pb
from pinkbombs import api, verify_token

GRAPHS = ["aqua-tonnes"]
TOKEN = "pinkbombs"

app = FastAPI()

app.include_router(
    api.router,
    prefix="/api/v1/secure",
    dependencies=[Depends(verify_token)]
)

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


# @app.get("/graphs/{graph_name}")
# async def read_item(graph_name):
#     if graph_name not in GRAPHS:
#         raise HTTPException(status_code=404, detail="Item not found")
#     df = pd.read_excel(
#         "data/atlantic_salmon-aquaculture_tonnes_live_weight_by_country_by_year.xlsx",
#     )
#     chart_obj=pb.make_area_chart(
#         df,
#         "ISO2 Code",
#         "Tonnes - live weight"
#     )
#     return {"graph_name": graph_name, "graph": chart_obj.to_json(), "path": "data/atlantic_salmon-aquaculture_tonnes_live_weight_by_country_by_year.xlsx"}