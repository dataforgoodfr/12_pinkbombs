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


def make_area_order_chart(input_df, input_x, input_y, input_col, title, reorder=False, 
                          palette=px.colors.qualitative.Pastel,
                          theme='simple_white') -> Figure:
    """Returns plotly express object as area chart with multiple lines
            Parameters:
                    input_df (pd.DataFrame): dataframe with data to be visualised 
                    input_x (str): name of the field for the x axis
                    input_y (str): name of the field for the y axis
                    input_col (str): name of the field for the colors
                    title (str): chart title
                    reorder (boolean): if true, dataframe is reodered by the input_col field, defauls is False 
                    palette (px.object): plotly discrete palette, default is Pastel
                    theme (str): plotly chart theme, default is 'simple_white'
            Returns:
                    area (plotly object): output chart object
    """ 
    # Data cleaning - TO REMOVE
    input_df[input_y] = input_df[input_y].str.replace(',', '.')
    input_df[input_y] = input_df[input_y].astype(float)

    if reorder:
        input_df_agg = input_df.groupby(input_col)[input_y].sum().sort_values(ascending=False)
        myorder = input_df_agg.reset_index()[input_col].tolist()
        input_df_u = input_df.set_index(input_col)
        input_df = input_df_u.loc[myorder].reset_index()

    area   = px.area(
        input_df,
        x=input_x,
        y=input_y,
        color=input_col,
        color_discrete_sequence=palette,
        )
    area.update_layout(template=theme, title=title)
    area.update_yaxes(exponentformat="none")
    return area


def make_color_bar_chart(input_df, input_x, input_y, input_col, title, xtitle,  
                   palette=px.colors.qualitative.Pastel1,
                   theme='simple_white') -> Figure:
    """Returns plotly express object as bar chart 
            Parameters:
                    input_df (pd.DataFrame): dataframe with data to be visualised 
                    input_x (str): name of the field for the x axis
                    input_y (str): name of the field for the y axis
                    input_col (str): name of the field to display in color
                    title (str): chart title
                    xtitle (str): x-axis title
                    palette (px.object): plotly discrete palette, default is Pastel
                    theme (str): plotly chart theme, default is 'simple_white'
            Returns:
                    bar (plotly object): output chart object
    """ 
    # Sort out number format
    input_df[input_x] = input_df[input_x].str.replace(',', '.')
    input_df[input_x] = input_df[input_x].astype(float)

    # Recalculate %
    input_df[input_col] = input_df[input_x]/input_df[input_x].sum()

    bar = px.bar(
        input_df,
        y=input_y,
        x=input_x,
        color=input_col,
        orientation='h',
        category_orders={input_y: input_df[input_y].to_list()},
        text_auto=',.0f',
        title=title,
        color_continuous_scale=px.colors.sequential.Burg,
        hover_name=input_y,
        hover_data={input_x:':,.0f', input_y:False, input_col:':.1%'}
        )
    bar.update_traces(textfont_size=12, textangle=0, 
                      textposition="outside", cliponaxis=False,)
    bar.update_layout(template='simple_white', xaxis_title=xtitle)
    bar.update_xaxes(exponentformat="none", range=[0, 2000000])
    bar.update_coloraxes(colorbar_tickformat='0%')

    return bar


def make_bar_chart(input_df, input_x, input_y, input_other, 
                          title, xtitle, palette=px.colors.qualitative.Pastel1,
                          theme='simple_white') -> Figure:
    """Returns plotly express object as bar chart with only 1 color
            Parameters:
                    input_df (pd.DataFrame): dataframe with data to be visualised 
                    input_x (str): name of the field for the x axis
                    input_y (str): name of the field for the y axis
                    input_other (str): name of other field to display on hover
                    title (str): chart title
                    xtitle (str): x-axis title
                    palette (px.object): plotly discrete palette, default is Pastel1
                    theme (str): plotly chart theme, default is 'simple_white'
            Returns:
                    bar (plotly object): output chart object
    """ 
    # Reorder dataframe
    input_df = input_df.sort_values(input_x, ascending=False)

    bar = px.bar(
        input_df,
        y=input_y,
        x=input_x,
        orientation='h',
        category_orders={input_y: input_df[input_y].to_list()},
        text_auto=',.0f',
        title=title,
        color_discrete_sequence=palette,
        hover_name=input_y,
        hover_data={input_x:':,.0f', input_y:False, input_other:True}
        )
    bar.update_traces(textfont_size=12, textangle=0, 
                      textposition="outside", cliponaxis=False,)
    bar.update_layout(template='simple_white', xaxis_title=xtitle)
    bar.update_xaxes(exponentformat="none")
    bar.update_coloraxes(colorbar_tickformat='0%')

    return bar