from utils.style import primary_color
from streamlit_lottie import st_lottie
from utils.lottie import load_lottieurl


def draw_header(st):
    # Original Lottie by https://lottiefiles.com/67736-big-data-analysis
    lottie_book = load_lottieurl(
        'https://assets3.lottiefiles.com/packages/lf20_sevxjflh.json')
    st_lottie(lottie_book, speed=1, height=200, key="initial")

    st.markdown(f"<h1 style='color:{primary_color}; font-family: Play;'>FACEIT Predictor Dashboard</h1>",
                unsafe_allow_html=True)
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """,
                unsafe_allow_html=True)
    st.markdown("""
<style>
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
          padding:16px;
          border: solid 4px transparent;
          border-radius: 4px;}
     .fp-selected-item {
          border-color: #fe6300;
     }
     .fp-item-logo {
          height:64px;
          margin: 16px auto;
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
<div style="padding:24px 0px 12px 0px">
    <div class="fp-flex-container">
        <div class="fp-flex-item">
            <img src="faceit_icon.png" class="fp-item-logo">
            <span class="fp-item-title">Ingestor</span>
            <span class="fp-item-description">Create a dataset of matches and players from the official FACEIT API.</span>
        </div>
        <div class="fp-flex-item fp-selected-item">
            <img src="machine_learning_icon.png" class="fp-item-logo">
            <span class="fp-item-title">Machine Learning</span>
            <span class="fp-item-description">Data Science workflow: process the data and create a model.</span>
        </div>
        <div class="fp-flex-item">
            <img src="api_icon.png" class="fp-item-logo">
            <span class="fp-item-title">Predictor API</span>
            <span class="fp-item-description">Implement the extension backend logic and database.</span>
        </div>
        <div class="fp-flex-item">
            <img src="browser_extension_icon.png" class="fp-item-logo">
            <span class="fp-item-title">Browser Extension</span>
            <span class="fp-item-description">Retrieves data to perform live predictions and contains frontend code.</span>
        </div>
        <div class="fp-flex-item">
            <img src="streamlit_icon.png" class="fp-item-logo">
            <span class="fp-item-title">Dashboard</span>
            <span class="fp-item-description">Streamlit app to monitor extension data.</span>
        </div>
    </div>
    <div class="arrow_box"></div>
</div>
""", unsafe_allow_html=True)
