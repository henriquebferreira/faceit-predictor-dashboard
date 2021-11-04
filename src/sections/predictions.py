import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
from utils import style_chart, weekdays_map
from components.prediction_bar import get_prediction_bar
import statistics
import joblib
from sections.base_section import Section
import streamlit as st
from db.loaders import load_orders


class PredictionsSection(Section):
    def __init__(self):
        super(PredictionsSection, self).__init__("Match Predictions")

    def core_draw(self):
        # Filter by user
        user_input = st.text_input("Filter by User (Ex: rapxim)", "")

        query_filter = {}
        if user_input:
            selected_user = self.db.users.find_one({"nickname": user_input})
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
                           category_orders={"day_of_week": list(weekdays_map().values())})
        style_chart(fig, chart_type='bar')
        col2.plotly_chart(fig, use_container_width=True)

        st.subheader("Predictions Probabilities")
        st.text("Sample Prediction")
        sample_bar_html = get_prediction_bar(
            "Map Name", "Team A Winning Probability ", "Team B Winning Probability ")
        st.markdown(sample_bar_html, unsafe_allow_html=True)

        # Filter by match Id
        match_id_input = st.text_input(
            "Get Predictions by Match Id (Ex:1-49f9a104-07af-44eb-a073-efbc2be4d1b4)", "")

        if match_id_input:
            match_document = self.db.matches.find_one({"_id": match_id_input})
            if match_document:
                match_predictions = match_document["predictions"]

                bar_html = ""
                for map_name, probabilities in match_predictions.items():
                    probabilities = [str(round(p*100, 1))
                                     for p in probabilities]
                    bar_html += get_prediction_bar(map_name,
                                                   probabilities[0], probabilities[1])

                st.markdown(bar_html, unsafe_allow_html=True)

                with st.expander("See Feature Values"):
                    features_document = self.db.features.find_one(
                        {"matchId": match_id_input})
                    if features_document:
                        features_df = pd.DataFrame(
                            features_document["globals"]).T
                        features_df.columns = ["Team A", "Team B"]
                        st.dataframe(features_df.style.format("{:.2f}"))
                    else:
                        st.error(
                            f'No features in database for match {match_id_input}')
            else:
                st.error(
                    f'No predictions in database for match {match_id_input}')

        trained_models = {
            "AdaBoost": 'adaboost',
            "Gradient Boosting": "gbc",
            "Linear Discriminant Analysis": "lda",
            "Logistic Regression": "lr",
            "Random Forest": "rf",
            "XGBoost": "xgb",
        }
        with st.form(key='prediction_form'):
            st.subheader("Feature Values")
            model = st.selectbox('Select Model', list(trained_models.keys()))
            c1, c2, c3 = st.columns(3)

            dif_mean_elo = c1.slider('Diff Mean ELO', -500.0, 500.0, 0.0)
            dif_mean_matches_on_map = c1.slider(
                'Diff Mean Matches on Map', -500.0, 500.0, 0.0)

            dif_mean_matches = c2.slider(
                'Diff Mean Matches', -500.0, 500.0, 0.0)
            dif_mean_kd_on_map = c2.slider(
                'Diff Mean KD on Map', -2.0, 2.0, 0.0)

            dif_mean_rating_prev = c3.slider(
                'Diff Mean Rating Recent', -2.0, 2.0, 0.0)
            mean_match_elo = c3.slider(
                'Mean Match Elo', 500.0, 3000.0, 2000.0)

            submit_button = c1.form_submit_button(label='Get Prediction')

        # create new prediction: set features values individually
        if submit_button:
            match_predictor = joblib.load(
                f'src/resources/models/{trained_models[model]}.joblib')
            sc = joblib.load('src/resources/models/scaler.bin')

            sample_features = np.zeros(47)
            sample_features[0] = mean_match_elo
            sample_features[1] = 1
            sample_features[2] = 0
            sample_features[3] = dif_mean_elo
            sample_features[8] = dif_mean_matches
            sample_features[13] = dif_mean_matches_on_map
            sample_features[15] = dif_mean_kd_on_map
            sample_features[31] = dif_mean_rating_prev
            sample_features[45] = 0
            sample_features[46] = 1
            scaled_features = sc.transform([sample_features])
            probs = match_predictor.predict_proba(scaled_features)[0]
            probs = [str(round(p*100, 1)) for p in probs]

            simulated_bar_html = get_prediction_bar(model, probs[0], probs[1])
            st.markdown(simulated_bar_html, unsafe_allow_html=True)
