import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.style import style_chart


def draw_predictions(st, db):
    matches_coll = db.matches
    features_coll = db.features
    orders_coll = db.orders
    users_coll = db.users

    # Recompute function only once per day
    @st.experimental_memo(ttl=24*3600)
    def load_orders():
        return list(orders_coll.find({}))

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
        title='Number of total orders over time',
        labels={
            "number_of_orders": "Number of Orders",
            "datetime": "Date"},
    )
    style_chart(fig, chart_type='line')
    st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(sorted_orders_by_timestamp,
                       x="hour",
                       labels={"hour": "Hour"},
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
                       category_orders={"day_of_week": list(weekdays_map.values())})
    style_chart(fig, chart_type='bar')
    st.plotly_chart(fig, use_container_width=True)
