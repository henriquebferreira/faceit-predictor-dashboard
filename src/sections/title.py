from streamlit_lottie import st_lottie
from components.lottie import load_lottie
from components.predictor_stages import get_predictor_stages
from sections.base_section import Section


class TitleSection(Section):
    def __init__(self):
        super(TitleSection, self).__init__(
            "FACEIT Predictor Dashboard", is_title=True)

    def core_draw(self):
        # Original Lottie by https://lottiefiles.com/67736-big-data-analysis
        st_lottie(load_lottie('lf20_sevxjflh'), height=200)

        stages_html = get_predictor_stages()
        self.st.markdown(stages_html, unsafe_allow_html=True)
