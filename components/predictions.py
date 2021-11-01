import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.style import style_chart
from utils.elements import draw_horizontal_line
import statistics


def draw_predictions(st, db):
    matches_coll = db.matches
    features_coll = db.features
    orders_coll = db.orders
    users_coll = db.users

    # Recompute function only once per day
    @st.experimental_memo(ttl=24*3600)
    def load_orders():
        return list(orders_coll.find({}))

    # Recompute function only once per day
    @st.experimental_memo(ttl=24*3600)
    def load_features():
        return list(features_coll.find({}).limit(1000))

    # Match Predictions
    st.header("Match Predictions")

    # Filter by user
    user_input = st.text_input("Filter by User", "")

    user_faceit_id = None
    if user_input:
        selected_user = users[users.nickname == user_input]
        if not selected_user.empty:
            user_faceit_id = selected_user.iloc[0].faceitId

    orders = pd.DataFrame(load_orders())
    orders_match = orders[orders.type == 'MATCH_PREDICT']
    if user_faceit_id:
        orders_match = orders_match[orders_match.userId == user_faceit_id]
    if user_input and not user_faceit_id:
        st.error(f'User {user_input} was not found')

    sorted_orders_by_timestamp = orders_match.sort_values(by="timestamp")

    sorted_orders_by_timestamp["datetime"] = sorted_orders_by_timestamp.timestamp.apply(
        lambda x: datetime.fromtimestamp(x))
    sorted_orders_by_timestamp["hour"] = sorted_orders_by_timestamp.datetime.apply(
        lambda x: x.hour)
    sorted_orders_by_timestamp["day_of_week"] = sorted_orders_by_timestamp.datetime.apply(
        lambda x: x.weekday())
    sorted_orders_by_timestamp["number_of_orders"] = range(
        1, len(sorted_orders_by_timestamp)+1)

    fig = px.line(
        data_frame=sorted_orders_by_timestamp,
        x='datetime',
        y="number_of_orders",
        title='Number of total predictions over time',
        labels={
            "number_of_orders": "Number of Orders",
            "datetime": "Date"},
    )
    style_chart(fig, chart_type='line')
    st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(sorted_orders_by_timestamp,
                       x="hour",
                       labels={"hour": "Hour"},
                       title="Predictions distribution by Hour",
                       histnorm='probability density')
    style_chart(fig, chart_type='bar')
    st.plotly_chart(fig, use_container_width=True)

    weekdays_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }
    sorted_orders_by_timestamp.day_of_week = sorted_orders_by_timestamp.day_of_week.map(
        weekdays_map)
    fig = px.histogram(sorted_orders_by_timestamp,
                       x="day_of_week",
                       labels={"day_of_week": "Day of week"},
                       histnorm='probability density',
                       title="Predictions distribution by Day of Week",
                       category_orders={"day_of_week": list(weekdays_map.values())})
    style_chart(fig, chart_type='bar')
    st.plotly_chart(fig, use_container_width=True)

    features = load_features()
    features_df = pd.DataFrame(features).drop("_id", axis=1)
    features_df = pd.concat([
        features_df.drop(['globals', 'maps'], axis=1),
        features_df['globals'].apply(pd.Series),
        features_df['maps'].apply(pd.Series)], axis=1)
    features_df["match_mean_elo"] = features_df.mean_elo.apply(
        lambda x: statistics.mean(x))

    fig = px.histogram(features_df,
                       x="match_mean_elo",
                       histnorm='probability density',
                       title="Predictions distribution by Match ELO",
                       labels={"match_mean_elo": "Match Mean Elo"},
                       nbins=50)
    style_chart(fig, chart_type='bar')
    st.plotly_chart(fig, use_container_width=True)

    # Filter by match Id
    match_id_input = st.text_input("Get Predictions by Match Id", "")
    if match_id_input:
        match_document = matches_coll.find_one({"_id": match_id_input})
        match_predictions = match_document["predictions"]
        bar_style = """
            <style>
                .predictor-weighted-bar {
                    display: flex;
                    text-align: center;
                    height: 16px;
                    font-size: 0px;
                    text-decoration: none;
                    color: white;
                    font-size: 14px;
                }

                .predictor-weighted-teambar {
                    line-height: 14px;
                }
                .predictor-background-lt {
                    background-color: #404040;
                }

                .predictor-background-gt {
                    background-color: #ff5500;
                }
            </style>"""
        st.markdown(bar_style, unsafe_allow_html=True)
        bar_html = ""
        for map_name, probabilities in match_predictions.items():
            bar_html += """
            <img src="https://cdn.faceit.com/static/stats_assets/csgo/maps/110x55/csgo-votable-maps-de_MAP_NAME-110x55.jpg">
            <div class="predictor-weighted-bar">
                <div class="predictor-weighted-teambar predictor-background-gt" style="flex-basis: PROB_A%">
                    PROB_A%
                </div>
                <div class="predictor-weighted-teambar predictor-background-lt" style="flex-basis: PROB_B%">
                    PROB_B%
                </div>
            </div>
            """
            bar_html = bar_html.replace(
                "PROB_A",  str(round((probabilities[0]*100), 1)))
            bar_html = bar_html.replace(
                "PROB_B",  str(round((probabilities[1]*100), 1)))
            bar_html = bar_html.replace(
                "MAP_NAME",  map_name)
        st.markdown(bar_html, unsafe_allow_html=True)

    draw_horizontal_line(st)
