import base64


def get_predictor_stages():
    stages_html = """
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
        </div>"""

    stages_icons = {
        "FACEIT_ICON_PLACEHOLDER": "src/resources/faceit_icon.png",
        "MACHINE_LEARNING_ICON_PLACEHOLDER": "src/resources/predictor_icon.png",
        "API_ICON_PLACEHOLDER": "src/resources/api_icon.png",
        "BROWSER_EXTENSION_ICON_PLACEHOLDER": "src/resources/browser_extension_icon.png",
        "STREAMLIT_ICON_PLACEHOLDER": "src/resources/streamlit_icon.png",
    }

    for placeholder, image_path in stages_icons.items():
        with open(image_path, "rb") as f:
            data_url = base64.b64encode(f.read()).decode("utf-8")
            stages_html = stages_html.replace(
                placeholder, f"data:image;base64,{data_url}")

    return stages_html
