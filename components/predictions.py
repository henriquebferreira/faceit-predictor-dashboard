import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.style import style_chart
from utils.elements import draw_horizontal_line
import statistics
import joblib

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

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(sorted_orders_by_timestamp,
                        x="hour",
                        labels={"hour": "Hour"},
                        title="Predictions distribution by Hour",
                        histnorm='probability density')
        style_chart(fig, chart_type='bar')
        col1.plotly_chart(fig, use_container_width=True)
    
    with col2:
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
                        y="day_of_week",
                        labels={"day_of_week": "Day of week"},
                        histnorm='probability density',
                        title="Predictions distribution by Day of Week",
                        category_orders={"day_of_week": list(weekdays_map.values())})
        style_chart(fig, chart_type='bar')
        col2.plotly_chart(fig, use_container_width=True)

    # features = load_features()
    # features_df = pd.DataFrame(features).drop("_id", axis=1)
    # features_df = pd.concat([
    #     features_df.drop(['globals', 'maps'], axis=1),
    #     features_df['globals'].apply(pd.Series),
    #     features_df['maps'].apply(pd.Series)], axis=1)
    # features_df["match_mean_elo"] = features_df.mean_elo.apply(
    #     lambda x: statistics.mean(x))

    # fig = px.histogram(features_df,
    #                 x="match_mean_elo",
    #                 histnorm='probability density',
    #                 title="Predictions distribution by Match ELO",
    #                 labels={"match_mean_elo": "Match Mean Elo"},
    #                 nbins=50)
    # style_chart(fig, chart_type='bar')
    # st.plotly_chart(fig, use_container_width=True)

    st.subheader("Predictions Probabilities")
    st.text("Sample Prediction")
    sample_bar_html ="""
        <div class="fp-prediction">
            <div class="fp-prediction-info">
                <div class="fp-sample-image-wrapper">
                    <img class="fp-sample-image" src="https://cdn.faceit.com/static/stats_assets/csgo/maps/110x55/csgo-votable-maps-de_mirage-110x55.jpg">
                </div>
                <span class="fp-map-name">Map Name</span>
            </div>
            <div class="fp-weighted-bar">
                <div class="fp-weighted-teambar fp-background-gt" style="flex-basis: 60%">
                    Team A Winning Probability
                </div>
                <div class="fp-weighted-teambar fp-background-lt" style="flex-grow: 1">
                    Team B Winning Probability
                </div>
            </div>
        </div>"""
    st.markdown(sample_bar_html, unsafe_allow_html=True)
    # Filter by match Id
    match_id_input = st.text_input("Get Predictions by Match Id", "1-49f9a104-07af-44eb-a073-efbc2be4d1b4")

    if match_id_input:
        match_document = matches_coll.find_one({"_id": match_id_input})
        if match_document:
            match_predictions = match_document["predictions"]

            bar_html = ""
            for map_name, probabilities in match_predictions.items():
                bar_html += """
                <div class="fp-prediction">
                     <div class="fp-prediction-info">
                        <div class="fp-sample-image-wrapper">
                            <img src="https://cdn.faceit.com/static/stats_assets/csgo/maps/110x55/csgo-votable-maps-de_MAP_NAME-110x55.jpg">
                        </div>
                        <span class="fp-map-name">MAP_NAME</span>
                    </div>
                    <div class="fp-weighted-bar">
                        <div class="fp-weighted-teambar fp-background-gt" style="flex-basis: PROB_A%">
                            PROB_A%
                        </div>
                        <div class="fp-weighted-teambar fp-background-lt" style="flex-grow: 1">
                            PROB_B%
                        </div>
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
        else:
            st.error(f'No predictions in database for match {match_id_input}')

    with st.expander("See Feature Values"):
        features_document = features_coll.find_one({"matchId": match_id_input})
        if features_document:
            features_df = pd.DataFrame(features_document["globals"]).T
            features_df.columns = ["Team A", "Team B"]
            st.dataframe(features_df.style.format("{:.2f}"))
        else:
            st.error(f'No features in database for match {match_id_input}')

    st.subheader("Feature Values")
    c1, c2, c3 = st.columns(3)

    dif_mean_elo = c1.slider('Diff Mean ELO', -500.0, 500.0, 0.0)
    dif_mean_matches_on_map = c1.slider('Diff Mean Matches on Map', -10.0, 10.0, 0.0)

    dif_mean_matches = c2.slider('Diff Mean Matches', -10.0, 10.0, 0.0)
    dif_mean_kd_on_map = c2.slider('Diff Mean KD on Map', -10.0, 10.0, 0.0)

    dif_mean_rating_prev = c3.slider('Diff Mean Rating Recent', -10.0, 10.0, 0.0)
    dif_mean_matches_on_day = c3.slider('Diff Mean Matches on Day', -10.0, 10.0, 0.0)

    
    ## create new prediction: set features values individually
    match_predictor = joblib.load('./ml_model.pkl')

    sample_features = [
    dif_mean_elo,
    0,
    0,
    0,
    0,
    dif_mean_matches,
    0,
    0,
    0,
    0,
    dif_mean_matches_on_map,
    0,
    dif_mean_kd_on_map,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    dif_mean_rating_prev,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    dif_mean_matches_on_day,
    0,
    0,
    0]
    simulated_probabilities = match_predictor.predict_proba([sample_features])[0]

    st.text("Prediction Probabilities for selected feature values")
    simulated_bar_html ="""
        <div class="fp-prediction">
            <div class="fp-prediction-info">
                <div class="fp-sample-image-wrapper">
                    <img class="fp-sample-image" src="https://cdn.faceit.com/static/stats_assets/csgo/maps/110x55/csgo-votable-maps-de_mirage-110x55.jpg">
                </div>
                <span class="fp-map-name">Map Name</span>
            </div>
            <div class="fp-weighted-bar">
                <div class="fp-weighted-teambar fp-background-gt" style="flex-basis: PROB_A%">
                    PROB_A%
                </div>
                <div class="fp-weighted-teambar fp-background-lt" style="flex-grow: 1">
                    PROB_B%
                </div>
            </div>
        </div>"""
    simulated_bar_html = simulated_bar_html.replace("PROB_A",  str(round((simulated_probabilities[0]*100), 1)))
    simulated_bar_html = simulated_bar_html.replace("PROB_B",  str(round((simulated_probabilities[1]*100), 1)))

    st.markdown(simulated_bar_html, unsafe_allow_html=True)
    draw_horizontal_line(st)
