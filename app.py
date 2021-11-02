import streamlit as st
from utils.db import get_mongo_db
from utils.style import add_stylesheet
from components.horizontal_line import draw_horizontal_line
from sections.header import draw_header
from sections.users import draw_users
from sections.predictions import draw_predictions


st.set_page_config(page_title="FACEIT Predictor Dashboard",
                   page_icon="images/page_icon.png")

add_stylesheet(st)

db = get_mongo_db(st)

draw_header(st)
draw_users(st, db)
draw_horizontal_line(st)
draw_predictions(st, db)
draw_horizontal_line(st)

