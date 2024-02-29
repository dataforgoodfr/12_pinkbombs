import altair as alt
import pandas as pd
import plotly.express as px


def make_geo(input_df, input_id, input_column, input_color_theme):
    geo = px.scatter_geo(
        input_df,
        locations=input_id,
        color=input_column,
        locationmode="country names",
        size=input_column,
        color_continuous_scale=input_color_theme,
        range_color=(0, max(input_df["Tonnes - live weight"])),
        projection="natural earth",
        labels={"Tonnes - live weight": "Tonnes"},
    )
    geo.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=350,
    )
    return geo


def make_area_chart(input_df, input_x, input_y, input_color_theme):
    group_df = input_df[[input_x, input_y]].groupby(input_x).sum().reset_index()
    group_df = group_df.sort_values(by=input_y, ascending=False).iloc[:5]
    area = px.area(
        input_df,
        x="Year",
        y="Tonnes - live weight",
        color="Country Name En",
        line_group="Country Name En",
    )

    px.bar(
        group_df,
        x=input_x,
        y=input_y,
        color=input_y,
        color_continuous_scale=input_color_theme,
        log_y=True,
    )
    return area


def make_donut(input_response, input_response_perc, input_text, input_color):
    if input_color == "blue":
        chart_color = ["#29b5e8", "#155F7A"]
    if input_color == "green":
        chart_color = ["#27AE60", "#12783D"]
    if input_color == "orange":
        chart_color = ["#F39C12", "#875A12"]
    if input_color == "red":
        chart_color = ["#E74C3C", "#781F16"]

    source = pd.DataFrame(
        {
            "Topic": ["", input_text],
            "% value": [100 - input_response_perc, input_response_perc],
        }
    )
    source_bg = pd.DataFrame(
        {
            "Topic": ["", input_text],
            "% value": [100, 0],
        }
    )

    plot = (
        alt.Chart(source)
        .mark_arc(innerRadius=45, cornerRadius=25)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(domain=[input_text, ""], range=chart_color),
                legend=None,
            ),
        )
        .properties(width=130, height=130)
    )

    text = plot.mark_text(
        align="center",
        color="#29b5e8",
        font="Lato",
        fontSize=32,
        fontWeight=700,
        fontStyle="italic",
    ).encode(text=alt.value(f"{input_response}"))
    plot_bg = (
        alt.Chart(source_bg)
        .mark_arc(innerRadius=45, cornerRadius=20)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(domain=[input_text, ""], range=chart_color),
                legend=None,
            ),
        )
        .properties(width=130, height=130)
    )
    return plot_bg + plot + text
