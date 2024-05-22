from config import MAPPING, MAPS
import argparse


def generate_graph(graph_name):
    if graph_name not in MAPPING:
        raise ValueError(f"Graph '{graph_name}' not found")
    df = MAPPING[graph_name]["parser"](
        "data/" + MAPPING[graph_name]["filename"],
    )
    chart_obj = MAPPING[graph_name]["function"](df, *MAPPING[graph_name]["arguments"])
    chart_obj.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return chart_obj.to_json()


def generate_maps(map_name):
    if map_name not in MAPS:
        raise ValueError(f"Map '{map_name}' not found")
    df = MAPS[map_name]["parser"](
        "data/" + MAPS[map_name]["filename"],
    )
    html_map = MAPS[map_name]["function"](df, *MAPS[map_name]["arguments"])
    return html_map


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-dir", default="./", help="Directory where to save the generated data")
    parser.add_argument("--graph-data", default="*", help="Graphs to generate, default is all graphs")
    parser.add_argument("--map-data", default="*", help="Maps to generate, default is all maps")
    
    args = parser.parse_args()

    inverse_mapping = {v["filename"]: k for k, v in MAPPING.items()}
    
    if args.graph_data == "*":
        new_graphs = list(MAPPING.keys())
    else:
        new_graphs = [inverse_mapping[filename] for filename in args.graph_data.split(",")]

    if args.map_data == "*":
        new_maps = list(MAPS.keys())
    else:
        new_maps = [inverse_mapping[filename] for filename in args.map_data.split(",")]
    
    print("new_graphs", new_graphs)
    print("new_maps", new_maps)

    
    