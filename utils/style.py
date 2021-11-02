import toml

st_config = toml.load(".streamlit/config.toml")
theme = st_config["theme"]
primary_color = theme["primaryColor"]
bg_color = theme["backgroundColor"]
secondary_bg_color = theme["secondaryBackgroundColor"]
text_color = theme["textColor"]


def style_chart(fig, chart_type):
    fig.update_yaxes(gridcolor=bg_color, gridwidth=4,
                     showline=False, zeroline=False)

    if chart_type == 'bar':
        fig.update_xaxes(showline=False)
        fig.update_traces(marker_color=primary_color)
        fig.update_layout(bargap=0.2)
    elif chart_type == 'line':
        fig.update_xaxes(gridcolor=bg_color, gridwidth=4, showline=False)
        fig.update_traces(line_color=primary_color)
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=40)
    )

def add_custom_style(st):
    st.markdown('<style>' + open('utils/style.css').read() + '</style>', unsafe_allow_html=True)