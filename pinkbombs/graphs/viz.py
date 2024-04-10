import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


def make_area_chart(input_df: pd.DataFrame, input_x: str, input_y: str) -> Figure:
    group_df = input_df[[input_x, input_y]].groupby(input_x).sum().reset_index()
    group_df = group_df.sort_values(by=input_y, ascending=False).iloc[:5]
    area = px.area(
        input_df,
        x="Year",
        y=input_y,
        color=input_x,
        line_group=input_x,
    )
    return area


def make_area_single_chart(input_df, input_x, input_y, title, 
                           palette=px.colors.qualitative.Pastel1,
                           theme='simple_white') -> Figure:
    """Returns plotly express object as area chart with a single line
            Parameters:
                    input_df (pd.DataFrame): dataframe with data to be visualised 
                    input_x (str): name of the field for the x axis
                    input_y (str): name of the field for the y axis
                    title (str): chart title
                    palette (px.object): plotly discrete palette, default is Pastel1
                    theme (str): plotly chart theme, default is 'simple_white'
            Returns:
                    area (plotly object): output chart object
    """ 
    area   = px.area(
        input_df,
        x=input_x,
        y=input_y,
        color_discrete_sequence=palette,
        )
    area.update_layout(template=theme, title=title)
    area.update_yaxes(exponentformat="none")
    return area