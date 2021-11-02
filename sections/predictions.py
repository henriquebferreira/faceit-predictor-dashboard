import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
from utils.style import style_chart
from components.horizontal_line import draw_horizontal_line
from components.prediction_bar import get_prediction_bar
import statistics
import joblib

def draw_predictions(st, db):
    weekdays_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    # Recompute function only once per day
    @st.experimental_memo(ttl=24*3600)
    def load_orders(query_filter):
        orders = pd.DataFrame(db.orders.find(query_filter))
        orders = orders[orders.type == 'MATCH_PREDICT']

        orders = orders.sort_values(by="timestamp")

        orders["datetime"] = orders.timestamp.apply(lambda x: datetime.fromtimestamp(x))
        orders["hour"] = orders.datetime.apply(lambda x: x.hour)

        orders["day_of_week"] = orders.datetime.apply(lambda x: x.weekday())
        orders.day_of_week = orders.day_of_week.map(weekdays_map)
        
        orders["number_of_orders"] = range(1, len(orders)+1)
        orders = orders.drop(columns=["_id","matchId", "type", "coinsBalance", "timestamp"], axis=1)
        
        return orders

    # Match Predictions
    st.header("Match Predictions")

    # Filter by user
    user_input = st.text_input("Filter by User (Ex: rapxim)", "")

    query_filter = {}
    if user_input:
        selected_user = db.users.find_one({"nickname":user_input})
        if selected_user:
            query_filter = {"userId": selected_user["faceitId"]}
        else:
            st.error(f'User {user_input} was not found')

            
    orders = load_orders(query_filter)

    fig = px.line(
        data_frame=orders,
        x='datetime',
        y="number_of_orders",
        title='Number of total predictions over time',
        labels={"number_of_orders": "Number of Orders",
        "datetime": "Date"})
    style_chart(fig, chart_type='line')
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    fig = px.histogram(orders,
                    x="hour",
                    labels={"hour": "Hour"},
                    title="Predictions distribution by Hour",
                    histnorm='probability density')
    style_chart(fig, chart_type='bar')
    col1.plotly_chart(fig, use_container_width=True)
    
    fig = px.histogram(orders,
                    y="day_of_week",
                    labels={"day_of_week": "Day of week"},
                    histnorm='probability density',
                    title="Predictions distribution by Day of Week",
                    category_orders={"day_of_week": list(weekdays_map.values())})
    style_chart(fig, chart_type='bar')
    col2.plotly_chart(fig, use_container_width=True)

    
    st.subheader("Predictions Probabilities")
    st.text("Sample Prediction")
    sample_bar_html = get_prediction_bar("Map Name", "Team A Winning Probability ", "Team B Winning Probability ")
    st.markdown(sample_bar_html, unsafe_allow_html=True)

    # Filter by match Id
    match_id_input = st.text_input("Get Predictions by Match Id (Ex:1-49f9a104-07af-44eb-a073-efbc2be4d1b4)", "")
    
    if match_id_input:
        match_document = db.matches.find_one({"_id": match_id_input})
        if match_document:
            match_predictions = match_document["predictions"]

            bar_html = ""
            for map_name, probabilities in match_predictions.items():
                probabilities = [str(round(p*100,1)) for p in probabilities]
                bar_html += get_prediction_bar(map_name, probabilities[0], probabilities[1])

            st.markdown(bar_html, unsafe_allow_html=True)

            with st.expander("See Feature Values"):
                features_document = db.features.find_one({"matchId": match_id_input})
                if features_document:
                    features_df = pd.DataFrame(features_document["globals"]).T
                    features_df.columns = ["Team A", "Team B"]
                    st.dataframe(features_df.style.format("{:.2f}"))
                else:
                    st.error(f'No features in database for match {match_id_input}')
        else:
            st.error(f'No predictions in database for match {match_id_input}')
    
    st.subheader("Feature Values")
    c1, c2, c3 = st.columns(3)

    dif_mean_elo = c1.slider('Diff Mean ELO', -500.0, 500.0, 0.0)
    dif_mean_matches_on_map = c1.slider('Diff Mean Matches on Map', -500.0, 500.0, 0.0)

    dif_mean_matches = c2.slider('Diff Mean Matches', -500.0, 500.0, 0.0)
    dif_mean_kd_on_map = c2.slider('Diff Mean KD on Map', -2.0, 2.0, 0.0)

    dif_mean_rating_prev = c3.slider('Diff Mean Rating Recent', -2.0, 2.0, 0.0)
    dif_mean_matches_on_day = c3.slider('Diff Mean Matches on Day', -5.0, 5.0, 0.0)
    
    
    ## create new prediction: set features values individually
    if st.button("Get Prediction"):
        match_predictor = joblib.load('./ml_model.pkl')

        sample_features = np.zeros(42)
        sample_features[0] = dif_mean_elo
        sample_features[5] = dif_mean_matches
        sample_features[10] = dif_mean_matches_on_map
        sample_features[12] = dif_mean_kd_on_map
        sample_features[26] = dif_mean_rating_prev
        sample_features[38] = dif_mean_matches_on_day

        simulated_probabilities = match_predictor.predict_proba([sample_features])[0]
        simulated_probabilities = [str(round(p*100,1)) for p in simulated_probabilities]

        simulated_bar_html = get_prediction_bar("Map Name", simulated_probabilities[0], simulated_probabilities[1])

        st.markdown(simulated_bar_html, unsafe_allow_html=True)