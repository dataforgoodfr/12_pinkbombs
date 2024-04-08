from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from pinkbombs.auth.authenicate import verify_token
import pinkbombs as pb
import pandas as pd

GRAPHS = ["tonnes"]

router = APIRouter()

@router.get("/")
async def ping(connection: bool = Depends(verify_token)):
    return {"status": "ok", "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%f")}

@router.get("/graphs/{graph_name}")
async def generate(graph_name, connection: bool = Depends(verify_token)):
    if graph_name not in GRAPHS:
        raise HTTPException(status_code=404, detail="Item not found")
    df = pd.read_excel(
        "data/atlantic_salmon-aquaculture_tonnes_live_weight_by_country_by_year.xlsx",
    )
    chart_obj=pb.make_area_chart(
        df,
        "ISO2 Code",
        "Tonnes - live weight"
    )
    return {"graph_name": graph_name, "graph": chart_obj.to_json(), "path": "data/atlantic_salmon-aquaculture_tonnes_live_weight_by_country_by_year.xlsx"}