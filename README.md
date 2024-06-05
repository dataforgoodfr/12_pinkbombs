Pinkbombs
================

This repository contains the pyhton code needed to generate the figure for the [Pinkbombs website](https://www.pinkbombs.org).

# Contributing

## Use Poetry

[Install Poetry](https://python-poetry.org/docs/):

    python3 -m pip install "poetry==1.4.0"

Install dependencies:

    poetry install

Add a dependency:

    poetry add pandas

Update dependencies:

    poetry update

## Use a venv 

    python3 -m venv name-of-your-venv

    source name-of-your-venv/bin/activate

## To launch pre-commits locally

[Install precommit](https://pre-commit.com/)

    pre-commit run --all-files 
 
## Test the code with Tox

    tox -vv

# How to
## Generate the graphs and maps
Activate your virtual environment:

    source name-of-your-venv/bin/activate

Run the generation script:

    python pinkbombs/generate.py

The graphs and maps will be added to the `data` directory. They are separated by type (`graphs`and `maps`) and by language (`fr`and `en`):
    
    data
    ├── graphs
    │   ├── en
    │   └── fr
    └── maps
        ├── en
        └── fr

Copy these to the [Pinkbombs webapp reppository](https://github.com/dataforgoodfr/12_pinkbombs_app) in the `public/dashboard/` directory.

**NOTE**: This is a temporary feature, when the images are moved to S3, a workflow will do this automatically upon merge.

## Adding a new visualization
To add a new graph or map, add a function that generates the visualization in the `pinkbombs/graphs/viz.py` or `pinkbombs/graphs/maps_viz.py` files respectively.

**The function NEEDS to return a Plotly Figure object for graphs or an html string for maps**

Make sure that the function is the import in the  `__init__.py` file in the graphs directory:

    from .viz import my_viz_function
    from .maps_viz import my_map_viz_function

The maps needs to the be added to the `config.py` file in order to have it automatically generated. Add the function to the correct section:

    MAPPING     -->     graphs/en
    MAPPINGFR   -->     graphs/fr
    MAPS        -->     maps/en
    MAPSFR      -->     maps/fr

__Be sure to add to both the french and english section.__

The function needs to be added in the following dictionary entry format:

    "visualisation-id": {
        "filename": "source-data.csv",
        "function": pb.my_viz_function,
        "parser": pd.read_csv, # or pd.read_excel for example
        "arguments": [ # add all the arguments in an ordered list
            "arg1",
            "arg2",
            "arg3",
            True,
            0
        ],
    },

Do not skip any argument to the function as these need to be in the correct order.

## Python scripts for testing your visualizations
To run the plotly graphs locally and generate html files you can view in your browser, you can use the script:

    python3 pinkbombs/graphs/test_graphs.py 

To translate the data and zip the csv files for download, run locally: 

    python3 pinkbombs/graphs/translate_data.py
    python3 pinkbombs/graphs/zip_data.py