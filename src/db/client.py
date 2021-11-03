import streamlit as st
from pymongo import MongoClient


@st.experimental_singleton
def get_mongo_db():
    mongo_secrets = st.secrets["mongo"]
    username = mongo_secrets["username"]
    password = mongo_secrets["password"]
    srv_connection = mongo_secrets["srv_connection"]

    connection_string = f"mongodb+srv://{username}:{password}@{srv_connection}"
    client = MongoClient(connection_string)
    db = client['faceit-predictor']

    return db
