import streamlit as st
import base64
import pathlib

import os

# Set up the Streamlit page
st.set_page_config(
    layout="wide", 
    page_title="Story - Pinkbombs",
    page_icon="🍣",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    body {
    background-image: url("http://localhost:8501/app/static/page_1.png");
    background-size: cover;
    }
</style>
""",
    unsafe_allow_html=True,
)


# st.cache(allow_output_mutation=True)

# def get_base64_of_bin_file(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# def set_png_as_page_bg(png_file):
#     bin_str = get_base64_of_bin_file(png_file)
#     page_bg_img = """

#     .stApp {
#     background-image: url(“data:image/jpeg;base64,%s”);
#     background-size: cover;
#     }

#     """ % bin_str

#     st.markdown(page_bg_img, unsafe_allow_html=True)
#     return


# set_png_as_page_bg("images/page_1.jpg")
# st.markdown(
#     f"""
#     <link rel="stylesheet" type="text/css" href="{image_uri}">
#     """,
#     unsafe_allow_html=True
# )
# st.markdown(
#     """
#     <style>
#     .reportview-container {
#         background: url(%s);
#     }
#    </style>
#     """ % image_uri,
#     unsafe_allow_html=True
# )



header_col = st.columns((0.1, 0.3, 1, 0.1, 0.1))
with header_col[0]:
    st.title("Pinkbombs")
with header_col[3]:
    if st.button("Data"):
        st.switch_page("pages/1_story.py")
with header_col[4]:
    if st.button("Story"):
        st.switch_page("main.py")
# # Create a container to hold the images
# image_container = st.container()

st.image("http://localhost:8501/app/static/page_1.png", use_column_width=True)

# # Add some content below the images
# st.write("This is some content below the scrolling background images.")
