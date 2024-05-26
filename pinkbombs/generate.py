from config import MAPPING, MAPS, MAPPINGFR, MAPSFR
import json

def generate_graph(graph_name, mapping):
    if graph_name not in mapping:
        raise ValueError(f"Graph '{graph_name}' not found")
    df = mapping[graph_name]["parser"](
        "data/" + mapping[graph_name]["filename"],
    )
    chart_obj = mapping[graph_name]["function"](df, *mapping[graph_name]["arguments"])
    chart_obj.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return chart_obj.to_json()


def generate_map(map_name, mapping):
    if map_name not in mapping:
        raise ValueError(f"Map '{map_name}' not found")
    df = mapping[map_name]["parser"](
        "data/" + mapping[map_name]["filename"],
    )
    html_map = mapping[map_name]["function"](df, *mapping[map_name]["arguments"])
    return html_map


if __name__ == "__main__":
    for graph_name in MAPPING:
        print(graph_name)
        graph_json = generate_graph(graph_name, MAPPING)
        with open(f"data/graphs/en/{graph_name}.json", "w") as f:
            json.dump(graph_json, f)

    for graph_name in MAPPINGFR:
        print(graph_name)
        graph_json = generate_graph(graph_name, MAPPINGFR)
        with open(f"data/graphs/fr/{graph_name}.json", "w") as f:
            json.dump(graph_json, f)

    for map_name in MAPS:
        print(map_name)
        map_json = generate_map(map_name, MAPS)
        with open(f"data/maps/en/{map_name}.html", "w") as f:
            f.write(map_json)

    for map_name in MAPSFR:
        print(map_name)
        map_json = generate_map(map_name, MAPSFR)
        with open(f"data/maps/fr/{map_name}.html", "w") as f:
            f.write(map_json)

    
    