import toml

st_config = toml.load(".streamlit/config.toml")
theme = st_config["theme"]
PRIMARY_COLOR = theme["primaryColor"]
BG_COLOR = theme["backgroundColor"]
SECONDARY_BG_COLOR = theme["secondaryBackgroundColor"]
TEXT_COLOR = theme["textColor"]


def style_chart(fig, chart_type):
    fig.update_yaxes(gridcolor=BG_COLOR, gridwidth=4,
                     showline=False, zeroline=False)
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=40))

    if chart_type == 'bar':
        fig.update_xaxes(showline=False)
        fig.update_traces(marker_color=PRIMARY_COLOR)
        fig.update_layout(bargap=0.2)
    elif chart_type == 'line':
        fig.update_xaxes(gridcolor=BG_COLOR, gridwidth=4, showline=False)
        fig.update_traces(line_color=PRIMARY_COLOR)
    elif chart_type == 'map':
        fig.update_geos(bgcolor= 'rgb(51, 51, 51)')

    

def add_stylesheet(st):
    st.markdown('<style>' + open('utils/style.css').read() + '</style>', unsafe_allow_html=True)