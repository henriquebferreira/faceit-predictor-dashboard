from db.client import get_mongo_db
from components.horizontal_line import draw_horizontal_line
import streamlit as st


class Section:
    def __init__(self, name, is_title=False):
        self.db = get_mongo_db()
        self.name = name
        self.st = st
        self.is_title = is_title

    def core_draw(self):
        pass

    def draw(self):
        st.title(self.name) if self.is_title else st.header(self.name)
        self.core_draw()
        draw_horizontal_line()
