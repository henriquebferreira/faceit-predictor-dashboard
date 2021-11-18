from datetime import datetime
import toml
import streamlit as st
import pycountry

st_config = toml.load(".streamlit/config.toml")
theme = st_config["theme"]
PRIMARY_COLOR = theme["primaryColor"]
BG_COLOR = theme["backgroundColor"]
SECONDARY_BG_COLOR = theme["secondaryBackgroundColor"]
TEXT_COLOR = theme["textColor"]


def style_chart(fig, chart_type):
    fig.update_yaxes(gridcolor=BG_COLOR, gridwidth=4,
                     showline=False, zeroline=False)
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=40))

    if chart_type == 'bar':
        fig.update_xaxes(showline=False)
        fig.update_traces(marker_color=PRIMARY_COLOR)
        fig.update_layout(bargap=0.2)
    elif chart_type == 'line':
        fig.update_xaxes(gridcolor=BG_COLOR, gridwidth=4, showline=False)
        fig.update_traces(line_color=PRIMARY_COLOR)
    elif chart_type == 'map':
        fig.update_geos(bgcolor='rgb(51, 51, 51)')
        fig.update_coloraxes(colorscale=[(0, "rgb(229, 236, 246)"), (0.2, "gray"),
                                         (0.5, "#fe6300"), (1, "#f50")])


def add_custom_css():
    st.markdown('<style>' + open('src/resources/style.css').read() +
                '</style>', unsafe_allow_html=True)


def timestamp_to_dt(ts):
    return datetime.fromtimestamp(ts)


def object_id_to_dt(obj_id):
    return obj_id.generation_time


def pct_change(new_val, old_val):
    return 100*(new_val-old_val)/old_val


def get_country_alpha_3(country_name):
    if country_name == 'XK':
        country_name = 'Kosovo'
    elif country_name == 'UAE':
        country_name = 'United Arab Emirates'
    close_countries = pycountry.countries.search_fuzzy(country_name)
    return close_countries[0].alpha_3


def weekdays_map():
    return {0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"}
