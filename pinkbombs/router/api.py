from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from pinkbombs.auth.authenicate import verify_token
from pinkbombs.config import MAPPING, MAPPINGFR, MAPS, MAPSFR
router = APIRouter()


@router.get("/")
async def ping():
    return {"status": "ok", "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%f")}


@router.get("/graphs/{graph_name}")
async def generate_graphs(graph_name, connection: bool = Depends(verify_token)):
    if graph_name not in MAPPING:
        raise HTTPException(status_code=404, detail="Graph not found")
    df = MAPPING[graph_name]["parser"](
        "data/" + MAPPING[graph_name]["filename"],
    )
    chart_obj = MAPPING[graph_name]["function"](df, *MAPPING[graph_name]["arguments"])
    
    return {
        "graph_name": graph_name,
        "graph": chart_obj.to_json(),
        "path": "data/" + MAPPING[graph_name]["filename"],
    }

@router.get("/fr/graphs/{graph_name}")
async def generate_graphs_fr(graph_name, connection: bool = Depends(verify_token)):
    if graph_name not in MAPPINGFR:
        raise HTTPException(status_code=404, detail="Graph not found")
    df = MAPPINGFR[graph_name]["parser"](
        "data/" + MAPPINGFR[graph_name]["filename"],
    )
    chart_obj = MAPPINGFR[graph_name]["function"](df, *MAPPINGFR[graph_name]["arguments"])
    return {
        "graph_name": graph_name,
        "graph": chart_obj.to_json(),
        "path": "data/" + MAPPINGFR[graph_name]["filename"],
    }

@router.get("/maps/{map_name}")
async def generate_maps(map_name, connection: bool = Depends(verify_token)):
    if map_name not in MAPS:
        raise HTTPException(status_code=404, detail="Map not found")
    df = MAPS[map_name]["parser"](
        "data/" + MAPS[map_name]["filename"],
    )
    html_map = MAPS[map_name]["function"](df, *MAPS[map_name]["arguments"])
    return {
        "map_name": map_name,
        "graph": html_map,
        "path": "data/" + MAPS[map_name]["filename"],
    }

@router.get("/fr/maps/{map_name}")
async def generate_maps_fr(map_name, connection: bool = Depends(verify_token)):
    if map_name not in MAPSFR:
        raise HTTPException(status_code=404, detail="Map not found")
    df = MAPSFR[map_name]["parser"](
        "data/" + MAPSFR[map_name]["filename"],
    )
    html_map = MAPSFR[map_name]["function"](df, *MAPSFR[map_name]["arguments"])
    return {
        "map_name": map_name,
        "graph": html_map,
        "path": "data/" + MAPSFR[map_name]["filename"],
    }
