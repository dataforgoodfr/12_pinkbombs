import numpy as np
import geopandas as gpd
import folium
from folium.plugins import GroupedLayerControl
from branca.element import Template, MacroElement


def get_transfo_param(df, col, min_rad=2.5, max_rad=60):
    """Returns the linear parameters to convert a dataframe field for display as bubble on a map
    Parameters:
            df (DataFrame): Dataframe containing data to display
            col (str): Name of the column to display as bubble on the map
            min_rad (float): min size of circle on the map, default is 2.5
            max_rad (float): min size of circle on the map, default is 60
    Returns:
            (slope, intercept) (pair): Pair of float as parameters of the linear transformation
    """
    minx = df[col].min()
    maxx = df[col].max()
    slope = (max_rad - min_rad) / (maxx - minx)
    intercept = max_rad - slope * maxx
    return (slope, intercept)


def make_geojson_layer(temp_geojson0, fields, aliases, mylistcol, modality, a, b):
    """Returns a folium layer with bubbles of size defined by a linear equation and pop-ups
    Parameters:
            temp_geojson0 (GeoJson DataFrame): Dataframe containing data to display
            fields (list(str)): List of fields to be shown on pop-ups
            aliases (list(str)): List of aliases to show the fields on pop-ups
            mylistcol (list(str)): List of colorcodes to use for the bubbles
            modality (str): Name of field used to determine size of bubbles
            a (float): Parameter for the slope of the linear transformation
            b (float): Parameter for the intercept of the linear transformation
    Returns:
            layer (folium object): Folium layer with bubbles and pop-ups settings
    """
    layer = folium.GeoJson(
        temp_geojson0,
        control=False,
        marker=folium.CircleMarker(
            radius=1, weight=2, color="black", fill_color="#000000", fill_opacity=0.6, opacity=0.8
        ),
        style_function=lambda x: {
            "fillColor": mylistcol[x["properties"]["Status_col"]],
            "color": mylistcol[x["properties"]["Status_col"]],
            "radius": (x["properties"][modality] * a + b),
            "fillOpacity": 0.6,
        },
        popup=folium.GeoJsonPopup(
            fields=fields,
            aliases=aliases,
            localize=True,
            labels=True,
            style="""background-color: #F0EFEF; border-radius: 3px; box-shadow: 3px;""",
            max_width=800,
        ),
    )
    return layer


def keep_4_figures(input):
    """Returns the number as string with only 3-4 significant figures"""
    if input >= 100:
        output = "{:,.0f}".format(input)
    elif input >= 10:
        output = "{:,.1f}".format(input)
    else:
        output = "{:,.2f}".format(input)
    return output


def create_elements_popups(input_df, french=False):
    """Returns the dataframe with all the fields necessary to make the pop-ups on the map
    Parameters:
            input_df (Geopandas DataFrame): Dataframe containing data to display
            french (boolean): Decide if aliases are in french. Default is False.
    Returns:
            input_df (Geopandas DataFrame): Dataframe with additionnal fields for the pop-ups
    """

    if french:
        status1="En fonctionnement"
        status2="En construction"
    else:
        status1="Operating"
        status2="In construction"

    # Simplify elec conso and calculate mid points
    input_df["elec_conso_GWh_low"] = input_df["elec_conso_kWh_low"] / 1e6
    input_df["elec_conso_GWh_high"] = input_df["elec_conso_kWh_high"] / 1e6
    input_df["elec_conso_GWh_mid"] = (
        input_df["elec_conso_GWh_high"] + input_df["elec_conso_GWh_low"]
    ) / 2
    input_df["carbon_kt_mid"] = (input_df["carbon_kt_high"] + input_df["carbon_kt_low"]) / 2

    # Create strings to display on box
    input_df["Production Capacity (annual)"] = (
        input_df["Production Max"].apply(lambda x: format(int(x), "8,d")) + " tonnes"
    )
    input_df["Electricity consumption (annual)"] = (
        input_df["elec_conso_GWh_low"].apply(lambda x: keep_4_figures(x))
        + " - "
        + input_df["elec_conso_GWh_high"].apply(lambda x: keep_4_figures(x))
        + " GWh"
    )
    input_df["Carbon Footprint (annual)"] = (
        input_df["carbon_kt_low"].apply(lambda x: keep_4_figures(x))
        + " - "
        + input_df["carbon_kt_high"].apply(lambda x: keep_4_figures(x))
        + " kilo tonnes C02"
    )
    input_df["Country carbon intensity of electricity"] = (
        input_df["Carbon intensity of electricity - gCO2/kWh"].apply(lambda x: format(x, ".0f"))
        + " gCO2/kWh"
        + input_df["Country"].apply(lambda x: " (" + x + ")")
    )

    # Create a field to combine Status and Detailed Status
    input_df["Detailed status ()"] = np.where(
        input_df["Detailed status"].isin([status1, status2]),
        "",
        input_df["Detailed status"].apply(lambda x: " (" + x + ")"),
    )
    input_df["Status2"] = input_df["Status"] + input_df["Detailed status ()"]

    # Create hyperlink for Location
    input_df["Location source link2"] = input_df["Location source"].apply(
        lambda x: f'<a href="{x}" target="_blank" rel="noopener noreferrer">'
    ) + input_df["Location"].apply(lambda x: f'{str(x)}</a>')

    # Create hyperlink for info/latest update
    input_df["Latest update2"] = input_df["Link info (no text)"].apply(
        lambda x: f'<a href="{x}" target="_blank" rel="noopener noreferrer">'
    ) + input_df["Latest update"].apply(
        lambda x: f'NAN</a>' if np.isnan(x) else f'{str(int(x))}</a>'
    )

    # Create hyperlink for the Carbon Electricity by country
    carbon_intensity_link = "https://ourworldindata.org/grapher/carbon-intensity-electricity"
    input_df["Country carbon intensity of electricity link"] = input_df[
        "Country carbon intensity of electricity"
    ].apply(lambda x: f'<a href="{carbon_intensity_link}" target="_blank" rel="noopener noreferrer">{x}</a>')

    # Define colors indeces
    input_df["Status_col"] = np.where(
        input_df["Status"] == status1,
        0,
        np.where(input_df["Status"] == status2, 1, 2),
    )

    return input_df


def define_fields(french=False):
    """Returns the fields and aliases to display in pop-ups
       Parameters:
            french (boolean): Decide if aliases are in french. Default is False.
        Returns:
            (fields, aliases) (tuple): two lists with the name of fields and aliases
    """
    # Choose fields to display in pop-up
    fields = [
        "Parent company",
        "Technologie",
        "Species",
        "Country",
        "Location source link2",
        "Status2",
        "Production Capacity (annual)",
        "Latest update2",
        "Electricity consumption (annual)",
        "Country carbon intensity of electricity link",
        "Carbon Footprint (annual)",
    ]
    if french:
        aliases = [
            "Producteur:",
            "Technologie:",
            "Espèces de saumon:",
            "Pays:",
            "Emplacement:",
            "État d'avancement:",
            "Capacité de production (annuelle):",
            "Dernière mise à jour identifiée:",
            "Consommation d'électricité (annuelle):",
            "Intensité carbone de l'électricité:",
            "Empreinte carbone (annuelle):",
        ]
    else :
        aliases = [
            "Company:",
            "Technology:",
            "Salmon species:",
            "Country:",
            "Location:",
            "Status:",
            "Production capacity (annual):",
            "Latest update found:",
            "Electricity consumption (annual):",
            "Carbon intensity of electricity:",
            "Carbon footprint (annual):",
        ]
    return (fields, aliases)


def define_colors():
    """Returns 2 lists of 3 colors for each Status"""
    shades_salmon = [
        "#C66264",  # deep salmon --> Operating
        "#fa8072",  # salmon --> In construction
        "#FEA993",  # light salmon --> Project
    ]
    shades_brown = [
        "#412829",  # deep brown --> Operating
        "#6e4546",  # brown --> In construction
        "#ac7b7d",  # light brown --> Project
    ]
    return (shades_salmon, shades_brown)


def make_title_html(map_title):
    """Returns a html title for the map"""
    title_html = """
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             """.format(map_title)
    return title_html


def make_legend_for_map(french=False):
    """Returns a html legend for the map - all hard-coded for now!
    Parameters:
            french (boolean): Decide if legend is in french. Default is False.
        Returns:
            template (html string): Legen in html format
    """

    template_gen = """
    {% macro html(this, kwargs) %}
    
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>jQuery UI Draggable - Default functionality</title>
      <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
    
      <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
      
      <script>
      $( function() {
        $( "#maplegend" ).draggable({
                        start: function (event, ui) {
                            $(this).css({
                                right: "auto",
                                top: "auto",
                                bottom: "auto"
                            });
                        }
                    });
    });
    
      </script>
    </head>
    <body>

    <div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:2px solid grey; 
     background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; left: 20px; bottom: 20px;'>
    """

    if french : 
        template_lang = """

        <div class='legend-subtitle'>Fermes par état d'avancement</div>
        
        <div class='legend-title'>Consommation d'électricité</div>
        
        <div class='legend-scale'>
        <ul class='legend-labels'>
            <li><span style='background:#C66264;opacity:0.7;'></span>En fonctionnement</li>
            <li><span style='background:#FA8072;opacity:0.7;'></span>En construction</li>
            <li><span style='background:#FEA993;opacity:0.7;'></span>En projet</li>
        
        <div class='legend-title'>Carbon footprint</div>
        
        <div class='legend-scale'>
        <ul class='legend-labels'>
            <li><span style='background:#412829;opacity:0.7;'></span>En fonctionnement</li>
            <li><span style='background:#6e4546;opacity:0.7;'></span>En construction</li>
            <li><span style='background:#ac7b7d;opacity:0.7;'></span>En projet</li>
        
        <li><a >La taille dépend de la production de la</a></li>
        <li><a >ferme, de la consommation d'électricité</a></li>
        <li><a >et de l'empreinte carbone estimées.</a></li>
        <li><a href='https://pinkbombs.org/about'>voir la Méthodologie</a></li>
        """
    else:
        template_lang = """

        <div class='legend-subtitle'>Land-based Farms by Status</div>
        
        <div class='legend-title'>Electricity Consumption</div>
        
        <div class='legend-scale'>
        <ul class='legend-labels'>
            <li><span style='background:#C66264;opacity:0.7;'></span>Operating</li>
            <li><span style='background:#FA8072;opacity:0.7;'></span>In construction</li>
            <li><span style='background:#FEA993;opacity:0.7;'></span>Project</li>
        
        <div class='legend-title'>Carbon footprint</div>
        
        <div class='legend-scale'>
        <ul class='legend-labels'>
            <li><span style='background:#412829;opacity:0.7;'></span>Operating</li>
            <li><span style='background:#6e4546;opacity:0.7;'></span>In construction</li>
            <li><span style='background:#ac7b7d;opacity:0.7;'></span>Project</li>
        
        <li><a >Size depends on farm production, estimated</a></li>
        <li><a >electricity consumption and carbon footprint</a></li>
        <li><a href='https://pinkbombs.org/about'>see Methodology</a></li>
        """

    template_gen2 = """
       </ul>
    </div>
    </div>
     
    </body>
    </html>

    <style type='text/css'>
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    {% endmacro %} 
    """

    template = template_gen + template_lang + template_gen2

    return template


def make_ras_bubble_map(
        input_df, 
        title_layer1,
        title_layer2,
        legend_title,
        title,
        add_title_legend=False, 
        french=False
        ):
    """Returns a folium map object with the RAS farms as bubble and pop-ups
    Parameters:
            input_df (DataFrame): Dataframe containing data to display
            title_layer1 (str): title for the map layer that appears first
            title_layer2 (str): title for the map layer that appears second
            legend_title (str): title of the legend grouping the 2 layers
            title (str): title for the map
            add_title_legend (boolean): turn true to add title and legend default is False
            french (boolean): Decide if aliases are in french. Default is False.
    Returns:
            map (folium object): Map with all elements
    """

    # Remove the 4 ambitions lines and convert to Geopandas
    input_df = input_df.loc[~input_df["Lat"].isna(),]
    input_gdf = gpd.GeoDataFrame(
        input_df, geometry=gpd.points_from_xy(input_df["Long"], input_df["Lat"]), crs="EPSG:4326"
    )

    # Create pop-ups
    input_gdf = create_elements_popups(input_gdf, french=french)

    # Determine transformation for display on the map - ELEC, CARBON
    (a_carbon, b_carbon) = get_transfo_param(input_gdf, "carbon_kt_mid", min_rad=3, max_rad=50)
    (a_elec, b_elec) = get_transfo_param(input_gdf, "elec_conso_GWh_mid", min_rad=3, max_rad=40)

    # Define fields, aliases and colors
    (fields, aliases) = define_fields(french=french)
    (shades_salmon, shades_brown) = define_colors()

    # Define the 2 layers for the modalities
    hg1 = folium.FeatureGroup(name=title_layer1)
    hg2 = folium.FeatureGroup(name=title_layer2)

    # Map centered on World - limit max zoom to avoid too much scrutiny
    map = folium.Map(
        location=(0, 0), maxZoom=12, minZoom=2,
        zoom_start=2, zoom_control=True, tiles="cartodb positron"
    )

    ## Apply to the 2 modalities - Electricity / Carbon
    for i in range(len(input_gdf.__geo_interface__["features"])):
        temp_geojson = {
            "features": [input_gdf.__geo_interface__["features"][i]],
            "type": "FeatureCollection",
        }

        # Elec
        temp_geojson_layer = make_geojson_layer(
            temp_geojson, fields, aliases, shades_salmon, "elec_conso_GWh_mid", a_elec, b_elec
        )
        temp_geojson_layer.add_to(hg1)

        # Carbon
        temp_geojson_layer = make_geojson_layer(
            temp_geojson, fields, aliases, shades_brown, "carbon_kt_mid", a_carbon, b_carbon
        )
        temp_geojson_layer.add_to(hg2)

    hg1.add_to(map)
    hg2.add_to(map)
    GroupedLayerControl(
        groups={legend_title: [hg1, hg2]},
        exclusive_groups=True,
        collapsed=False,
    ).add_to(map)

    # Add scrollzoom toggler
    folium.plugins.ScrollZoomToggler().add_to(map)

    if add_title_legend:
        map_title = title
        map.get_root().html.add_child(folium.Element(make_title_html(map_title)))

        legend_temp = make_legend_for_map(french=french)
        macro = MacroElement()
        macro._template = Template(legend_temp)
        map.get_root().add_child(macro)

    return map.get_root().render()
