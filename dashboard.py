from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
from utils.style import style_chart, primary_color, bg_color, secondary_bg_color, text_color
from pymongo import MongoClient, DESCENDING
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from components.header import draw_header
from components.users import draw_users
from components.predictions import draw_predictions


st.set_page_config(page_title="FACEIT Predictor Dashboard",
                   page_icon="icon-borderless-big.png")


@st.experimental_singleton
def get_database_session(section):
    # Create a database session object that points to the URL.
    mongo_secrets = st.secrets[section]
    username = mongo_secrets["username"]
    password = mongo_secrets["password"]
    srv_connection = mongo_secrets["srv_connection"]

    connection_string = f"mongodb+srv://{username}:{password}@{srv_connection}"
    client = MongoClient(connection_string)
    db = client['faceit-predictor']
    return db


db = get_database_session("mongo")

matches_coll = db.matches
features_coll = db.features
orders_coll = db.orders
users_coll = db.users


draw_header(st)
draw_users(st, db)
draw_predictions(st, db)


# Predictions
