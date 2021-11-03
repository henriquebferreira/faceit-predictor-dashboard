import streamlit as st
from sections.sections import draw_sections
from utils import add_custom_css


def main():
    st.set_page_config(page_title="FACEIT Predictor Dashboard",
                       page_icon="src/resources/page_icon.png")
    add_custom_css()
    draw_sections()


if __name__ == "__main__":
    main()
