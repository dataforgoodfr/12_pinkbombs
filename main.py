import altair as alt
import pandas as pd
import streamlit as st

import pinkbombs as pb

st.set_page_config(
    page_title="Pinkbombs",
    page_icon="🍣",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("# Pinkbombs")

alt.themes.enable("dark")

df_reshaped = pd.read_excel(
    "data/atlantic_salmon-aquaculture_tonnes_live_weight_by_country_by_year.xlsx",
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

col = st.columns((1.5, 4.5, 2), gap="medium")

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

    st.markdown("#### Tonnage Difference > 1000")

    # Filter countries with population difference > 1000
    df_greater_1000 = df_tonnage_difference_sorted[
        df_tonnage_difference_sorted.tonnage_difference > 1000
    ]
    df_less_1000 = df_tonnage_difference_sorted[
        df_tonnage_difference_sorted.tonnage_difference < -1000
    ]

    # % of countries with population difference > 1000
    countries_difference_greater = round(
        (
            len(df_greater_1000)
            / df_tonnage_difference_sorted["Country Name En"].nunique()
        )
        * 100,
    )
    countries_difference_less = round(
        (len(df_less_1000) / df_tonnage_difference_sorted["Country Name En"].nunique())
        * 100,
    )

    donut_chart_greater = pb.make_donut(
        len(df_greater_1000),
        countries_difference_greater,
        "Max Increase",
        "red",
    )
    donut_chart_less = pb.make_donut(
        len(df_less_1000),
        countries_difference_less,
        "Min Increase",
        "blue",
    )

    differences_col = st.columns((0.2, 1, 0.2))
    with differences_col[1]:
        st.write("Increase")
        st.altair_chart(donut_chart_greater)
        st.write("Decrease")
        st.altair_chart(donut_chart_less)


with col[1]:
    st.markdown("#### Total Tonnage")

    choropleth = pb.make_geo(
        df_selected_year,
        "Country Name En",
        "Tonnes - live weight",
        selected_color_theme,
    )
    st.plotly_chart(choropleth, use_container_width=True)
    st.markdown("##### Top 5 Countries")
    area_chart = pb.make_area_chart(
        df_reshaped,
        "Country Name En",
        "Tonnes - live weight",
        selected_color_theme,
    )
    st.plotly_chart(area_chart, use_container_width=True)


with col[2]:
    st.markdown("#### Top States")

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
