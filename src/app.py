import streamlit as st
from utils.style import add_custom_css
from sections.sections import draw_sections


def main():
    st.set_page_config(page_title="FACEIT Predictor Dashboard",
                       page_icon="resources/page_icon.png")
    add_custom_css()
    draw_sections()


if __name__ == "__main__":
    main()
