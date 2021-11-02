import requests
import streamlit as st
from streamlit_lottie import st_lottie

@st.experimental_memo
def load_lottie(resource_id):
    r = requests.get(f'https://assets3.lottiefiles.com/packages/{resource_id}.json')
    if r.status_code != 200:
        return None
    return r.json()
