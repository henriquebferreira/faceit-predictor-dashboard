from utils.db import get_mongo_db
import streamlit as st


class Section:
    def __init__(self, title, is_header=False):
        self.db = get_mongo_db()
        self.title = title
        self.st = st
        self.is_header = is_header

    def core_draw(self):
        pass

    def draw(self):
        st.title(self.title) if self.is_header else st.header(self.title)
        self.core_draw()
