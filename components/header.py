from utils.style import primary_color
from streamlit_lottie import st_lottie
from utils.lottie import load_lottieurl
from utils.elements import draw_horizontal_line
import base64


def draw_header(st):
    # Original Lottie by https://lottiefiles.com/67736-big-data-analysis
    lottie_book = load_lottieurl(
        'https://assets3.lottiefiles.com/packages/lf20_sevxjflh.json')
    st_lottie(lottie_book, speed=1, height=200, key="initial")

    st.markdown(f"<h1 style='color:{primary_color}; font-family: Play;'>FACEIT Predictor Dashboard</h1>",
                unsafe_allow_html=True)

    stages_html = """
<style>
     .fp-stages-container {
         display: flex;
        flex-direction: column;
        padding: 24px 0px 12px;
        width: 75vw;
        position: relative;
        left: 50%;
        transform: translate(-50%, 0%);}
     .fp-flex-container {
          display: flex;
          flex-direction: row;
          justify-content: space-evenly;
          flex-wrap:nowrap;
          width: 100%;
          font-family: 'Play';}
     .fp-flex-item {
          display:flex;
          flex-direction: column;
          flex: 1 1 0px;
          padding: 8px;
          border: solid 4px transparent;
          border-radius: 4px;}
     .fp-selected-item {
          border-color: #fe6300;
     }
     .fp-item-logo {
          height:64px;
          margin: 4px auto;
     }
     .fp-item-title {
          color: #ff5500;
          font-size: 18px;
          font-weight: bold;
          text-align: center;
          padding-bottom: 8px;
     }
     .fp-item-description {
          color: white;
          font-size: 14px;
     }
     .arrow_box {
          height:4px;
          margin:18px 32px;
          position: relative;
          background:linear-gradient(90deg, gray 20%, #ff5500 80%);}
     .arrow_box:before {
          left: 100%;
          top: 50%;
          border: solid transparent;
          content: "";
          position: absolute;
          pointer-events: none;
     }
     .arrow_box:before {
          border-left-color: #ff5500;
          border-width: 12px;
          margin-top: -12px;
     }
</style>
<div class="fp-stages-container">
    <div class="fp-flex-container">
        <div class="fp-flex-item">
            <img src="FACEIT_ICON_PLACEHOLDER" class="fp-item-logo">
            <span class="fp-item-title">Ingestor</span>
            <span class="fp-item-description">Create a dataset of matches and players from the official FACEIT API.</span>
        </div>
        <div class="fp-flex-item">
            <img src="MACHINE_LEARNING_ICON_PLACEHOLDER" class="fp-item-logo">
            <span class="fp-item-title">Machine Learning</span>
            <span class="fp-item-description">Data Science workflow: process the data and create a model.</span>
        </div>
        <div class="fp-flex-item">
            <img src="API_ICON_PLACEHOLDER" class="fp-item-logo">
            <span class="fp-item-title">Predictor API</span>
            <span class="fp-item-description">Implement the extension backend logic and database.</span>
        </div>
        <div class="fp-flex-item">
            <img src="BROWSER_EXTENSION_ICON_PLACEHOLDER" class="fp-item-logo">
            <span class="fp-item-title">Extension</span>
            <span class="fp-item-description">Retrieves data to perform live predictions and contains frontend code.</span>
        </div>
        <div class="fp-flex-item fp-selected-item">
            <img src="STREAMLIT_ICON_PLACEHOLDER" class="fp-item-logo">
            <span class="fp-item-title">Dashboard</span>
            <span class="fp-item-description">Streamlit app to monitor extension data.</span>
        </div>
    </div>
    <div class="arrow_box"></div>
</div>
"""
    stages_icons = {
        "FACEIT_ICON_PLACEHOLDER": "faceit_icon.png",
        "MACHINE_LEARNING_ICON_PLACEHOLDER": "machine_learning_icon.png",
        "API_ICON_PLACEHOLDER": "api_icon.png",
        "BROWSER_EXTENSION_ICON_PLACEHOLDER": "browser_extension_icon.png",
        "STREAMLIT_ICON_PLACEHOLDER": "streamlit_icon.png",
    }

    for placeholder, image_path in stages_icons.items():
        with open(image_path, "rb") as f:
            data_url = base64.b64encode(f.read()).decode("utf-8")
            stages_html = stages_html.replace(
                placeholder, f"data:image;base64,{data_url}")
    st.markdown(stages_html, unsafe_allow_html=True)

    draw_horizontal_line(st)
