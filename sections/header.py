from streamlit_lottie import st_lottie
from components.lottie import load_lottie
from components.predictor_stages import draw_predictor_stages
from components.horizontal_line import draw_horizontal_line

def draw_header(st):
    # Original Lottie by https://lottiefiles.com/67736-big-data-analysis
    st_lottie(load_lottie('lf20_sevxjflh'), height=200)

    st.title("FACEIT Predictor Dashboard")

    draw_predictor_stages(st)