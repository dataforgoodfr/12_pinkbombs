from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from pinkbombs.auth.authenicate import verify_token
from pinkbombs.config import MAPPING
import pandas as pd

router = APIRouter()

@router.get("/")
async def ping():
    return {"status": "ok", "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%f")}

@router.get("/graphs/{graph_name}")
async def generate(graph_name, connection: bool = Depends(verify_token)):
    if graph_name not in MAPPING:
        raise HTTPException(status_code=404, detail="Graph not found")
    df = MAPPING[graph_name]["parser"](
        "data/"+MAPPING[graph_name]["filename"],
    )
    chart_obj= MAPPING[graph_name]["function"](df, *MAPPING[graph_name]["arguments"])
    return {
        "graph_name": graph_name, "graph": chart_obj.to_json(), 
        "path": "data/"+MAPPING[graph_name]["filename"],
    }