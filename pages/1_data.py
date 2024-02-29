import altair as alt
import pandas as pd
import streamlit as st

import pinkbombs as pb

st.set_page_config(
    page_title="Data - Pinkbombs",
    page_icon="🍣",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

header_col = st.columns((0.3, 0.8, 0.1, 0.1, 0.1, 0.1))
with header_col[0]:
    st.markdown("# Pinkbombs")
with header_col[2]:
    if st.button("Story"):
        st.switch_page("main.py")
with header_col[3]:
    if st.button("Data"):
        st.switch_page("pages/1_data.py")
with header_col[4]:
    if st.button("Act"):
        st.switch_page("main.py")
with header_col[5]:
    if st.button("About"):
        st.switch_page("pages/1_data.py")
    

alt.themes.enable("dark")

df_reshaped = pd.read_excel(
    "data/atlantic_salmon-aquaculture_tonnes_live_weight_by_country_by_year.xlsx",
)

lorem = "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quia, non, corrupti ut illum eius et fugiat impedit id quod recusandae quo accusamus laborum explicabo sint quam cupiditate quos! At tenetur ipsam dicta. Explicabo repellat fugit alias deleniti quaerat facere expedita deserunt eum dolores ..."


st.markdown("<h3>En un coup d'oeil</h3>", unsafe_allow_html=True)

columns = [0.2, 1]*4 + [0.2]
headline_columns = st.columns(columns, gap="large")
with headline_columns[1]:
    st.markdown("<h4 style='text-align: center;'>XXX</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Saumons consommés en France cette année.</p>", unsafe_allow_html=True)
with headline_columns[3]:
    st.markdown("<h4 style='text-align: center;'>13 000 000</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Saumons consommés en France cette année.</p>", unsafe_allow_html=True)
with headline_columns[5]:
    st.markdown("<h4 style='text-align: center;'>11.1%</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Croissance de la consommation mondiale depuis 10 ans.</p>", unsafe_allow_html=True)
with headline_columns[7]:
    st.markdown("<h4 style='text-align: center;'>120 Gt de CO2</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Impact carbone de l'industrie du Saumon sur l'année passée.</p>", unsafe_allow_html=True)
    
st.markdown("<h3>En une seconde</h3>", unsafe_allow_html=True)

columns = [0.3, 0.7, 0.1]*4 + [0.3]
headline_columns = st.columns(columns, gap="small")
with headline_columns[1]:
    st.markdown(":fish: **Indicateur a.1**", unsafe_allow_html=True)
    st.markdown(":whale: **Indicateur a.2**", unsafe_allow_html=True)
    st.markdown(":sushi: **Indicateur a.3**", unsafe_allow_html=True)
    st.markdown(":tropical_fish: **Indicateur a.4**", unsafe_allow_html=True)
with headline_columns[2]:
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
with headline_columns[4]:
    st.markdown(":earth_africa: **Indicateur b.1**", unsafe_allow_html=True)
    st.markdown(":herb: **Indicateur b.2**", unsafe_allow_html=True)
    st.markdown(":recycle: **Indicateur b.3**", unsafe_allow_html=True)
    st.markdown(":sos: **Indicateur b.4**", unsafe_allow_html=True)
with headline_columns[5]:
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
with headline_columns[7]:
    st.markdown(":fish: **Indicateur c.1**", unsafe_allow_html=True)
    st.markdown(":fish: **Indicateur c.2**", unsafe_allow_html=True)
    st.markdown(":fish: **Indicateur c.3**", unsafe_allow_html=True)
    st.markdown(":fish: **Indicateur c.4**", unsafe_allow_html=True)
with headline_columns[8]:
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
with headline_columns[10]:
    st.markdown(":fish: **Indicateur d.1**", unsafe_allow_html=True)
    st.markdown(":fish: **Indicateur d.2**", unsafe_allow_html=True)
    st.markdown(":fish: **Indicateur d.3**", unsafe_allow_html=True)
    st.markdown(":fish: **Indicateur d.4**", unsafe_allow_html=True)
with headline_columns[11]:
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)
    st.markdown("<p>XXX</p>", unsafe_allow_html=True)



st.markdown("<h2>Disparition des saumons sauvages</h2>", unsafe_allow_html=True)

graph_columns1 = st.columns((0.1, 0.5, 0.1, 0.5, 0.1), gap="medium")
with graph_columns1[1]:
    st.markdown("<h4 style='text-align: center;'>Etat de stock de saumon sauvage</h4>", unsafe_allow_html=True)
    area_chart = pb.make_area_chart(
        df_reshaped,
        "Country Name En",
        "Tonnes - live weight"
    )
    st.plotly_chart(area_chart, use_container_width=True)
with graph_columns1[3]:    
    st.markdown(
        """
    <style>
        [data-testid="column"] {
            display: flex;
            # flex-direction: column;
            align-items: center;
            justify-content: center;

        }
    </style>""" + f"<p style='text-align: center;'>{lorem}</p>",
        unsafe_allow_html=True,
    )

st.markdown("<h2>Hyper-croissance de l'evelage de saumons</h2>", unsafe_allow_html=True)

graph_columns2 = st.columns((0.1, 0.5, 0.1, 0.6, 0.1), gap="medium")
with graph_columns2[3]:
    st.markdown("<h4 style='text-align: center;'>Production de saumon d'élevage</h4>", unsafe_allow_html=True)
    area_chart = pb.make_area_chart(
        df_reshaped,
        "Country Name En",
        "Tonnes - live weight"
    )
    st.plotly_chart(area_chart, use_container_width=True)
with graph_columns2[1]:    
    st.markdown(
        """
    <style>
        [data-testid="column"] {
            display: flex;
            # flex-direction: column;
            align-items: center;
            justify-content: center;

        }
    </style>""" + f"<p style='text-align: center;'>{lorem}</p>",
        unsafe_allow_html=True,
    )

st.markdown("<h2>Super-concentration des zones de production</h2>", unsafe_allow_html=True)
_col = st.columns((0.2, 1, 0.2), gap="medium")
with _col[1]:
    st.markdown(
        """
    <style>
        [data-testid="column"] {
            display: flex;
            # flex-direction: column;
            align-items: center;
            justify-content: center;

        }
    </style>""" + f"<p style='text-align: center;'>{lorem}</p>",
        unsafe_allow_html=True,
    )

button_col = st.columns((0.15, 0.15, 1, 0.2))

year_list = df_reshaped.Year.unique()
year_list.sort()
year_list = year_list.tolist()

with button_col[0]:

    selected_year = st.selectbox("Select a year", year_list, index=len(year_list) - 1)
    df_selected_year = df_reshaped[df_reshaped.Year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(
        by="Tonnes - live weight",
        ascending=False,
    )
with button_col[1]:
    color_theme_list = [
        "blues",
        "cividis",
        "greens",
        "inferno",
        "magma",
        "plasma",
        "reds",
        "rainbow",
        "turbo",
        "viridis",
    ]
    selected_color_theme = st.selectbox("Select a color theme", color_theme_list)

choropleth = pb.make_geo(
    df_selected_year,
    "Country Name En",
    "Tonnes - live weight",
    selected_color_theme,
)
st.plotly_chart(choropleth, use_container_width=True)


col = st.columns((2, 2), gap="medium")

with col[0]:
    st.markdown("#### Max/Min Increase in Tonnage")

    df_tonnage_difference_sorted = pb.calculate_tonnage_difference(
        df_reshaped,
        selected_year,
    )

    first_country_name = df_tonnage_difference_sorted["Country Name En"].iloc[0]
    first_country_population = pb.format_number(
        df_tonnage_difference_sorted["Tonnes - live weight"].iloc[0],
    )
    first_country_delta = pb.format_number(
        df_tonnage_difference_sorted.tonnage_difference.iloc[0],
    )

    st.metric(
        label=first_country_name,
        value=first_country_population,
        delta=first_country_delta,
    )

    last_country_name = df_tonnage_difference_sorted["Country Name En"].iloc[-1]
    last_country_population = pb.format_number(
        df_tonnage_difference_sorted["Tonnes - live weight"].iloc[-1],
    )
    last_country_delta = pb.format_number(
        df_tonnage_difference_sorted.tonnage_difference.iloc[-1],
    )

    st.metric(
        label=last_country_name,
        value=last_country_population,
        delta=last_country_delta,
    )

    # st.markdown("#### Tonnage Difference > 1000")

    # # Filter countries with population difference > 1000
    # df_greater_1000 = df_tonnage_difference_sorted[
    #     df_tonnage_difference_sorted.tonnage_difference > 1000
    # ]
    # df_less_1000 = df_tonnage_difference_sorted[
    #     df_tonnage_difference_sorted.tonnage_difference < -1000
    # ]

    # # % of countries with population difference > 1000
    # countries_difference_greater = round(
    #     (
    #         len(df_greater_1000)
    #         / df_tonnage_difference_sorted["Country Name En"].nunique()
    #     )
    #     * 100,
    # )
    # countries_difference_less = round(
    #     (len(df_less_1000) / df_tonnage_difference_sorted["Country Name En"].nunique())
    #     * 100,
    # )

    # donut_chart_greater = pb.make_donut(
    #     len(df_greater_1000),
    #     countries_difference_greater,
    #     "Max Increase",
    #     "red",
    # )
    # donut_chart_less = pb.make_donut(
    #     len(df_less_1000),
    #     countries_difference_less,
    #     "Min Increase",
    #     "blue",
    # )

    # differences_col = st.columns((0.2, 1, 0.2))
    # with differences_col[1]:
    #     st.write("Increase")
    #     st.altair_chart(donut_chart_greater)
    #     st.write("Decrease")
    #     st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown("#### Top Countries")

    st.dataframe(
        df_selected_year_sorted,
        column_order=("Country Name En", "Tonnes - live weight"),
        hide_index=True,
        width=None,
        column_config={
            "Country Name En": st.column_config.TextColumn(
                "Country",
            ),
            "Tonnes - live weight": st.column_config.ProgressColumn(
                "Acquaculture Tonnage",
                format="%f.2",
                min_value=0,
                max_value=max(df_selected_year_sorted["Tonnes - live weight"]),
            ),
        },
    )

with st.expander("About", expanded=True):
    st.write(
        """
        - Data: FAO
        - :orange[**Max/Min Increase in Tonnage**]: Country with the highest/lowest increase in tonnage.
        - :orange[**Tonnage Difference > 1000**]: Number of countries with tonnage difference greater than 1000.
        """,
    )
