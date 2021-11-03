from streamlit_lottie import st_lottie
from components.lottie import load_lottie
from components.predictor_stages import get_predictor_stages
from sections.base_section import Section
import streamlit as st


class HeaderSection(Section):
    def __init__(self):
        super(HeaderSection, self).__init__(
            "FACEIT Predictor Dashboard", is_header=True)

    def core_draw(self):
        # Original Lottie by https://lottiefiles.com/67736-big-data-analysis
        st_lottie(load_lottie('lf20_sevxjflh'), height=200)

        stages_html = get_predictor_stages()
        st.markdown(stages_html, unsafe_allow_html=True)
