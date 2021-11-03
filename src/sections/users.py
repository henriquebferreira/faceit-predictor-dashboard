import pandas as pd
from datetime import datetime
import pycountry
from dateutil.relativedelta import relativedelta
import plotly.express as px
from utils.style import style_chart
from components.horizontal_line import draw_horizontal_line
from utils.metrics import pct_change, get_users_metrics
from sections.base_section import Section
import streamlit as st


class UsersSection(Section):
    def __init__(self):
        super(UsersSection, self).__init__("Users")

    def core_draw(self):
        def get_country_alpha_3(country_name):
            if country_name == 'XK':
                country_name = 'Kosovo'
            elif country_name == 'UAE':
                country_name = 'United Arab Emirates'
            close_countries = pycountry.countries.search_fuzzy(country_name)
            return close_countries[0].alpha_3

        @st.experimental_memo(ttl=3600)
        def load_users():
            users = pd.DataFrame(self.db.users.find({}))
            users["createdAtDt"] = users.createdAt.apply(
                lambda x: datetime.fromtimestamp(x))
            users = users.sort_values(by="createdAtDt")
            users["number_of_users"] = range(1, len(users)+1)
            users = users.drop(columns=["_id", "faceitId", "email"])
            return users

        @st.experimental_memo(ttl=3600)
        def get_most_active_users():
            most_active_users_cursor = self.db.orders.aggregate(
                [
                    {"$group": {"_id": "$userId", "num_orders": {"$sum": 1}}},
                    {"$sort": {"num_orders": -1}},
                    {"$limit": 15},
                    {"$lookup":
                     {
                         "from": "users",
                         "localField": "_id",
                         "foreignField": "faceitId",
                         "as": "fromUsers"
                     }
                     },
                    {"$replaceRoot": {"newRoot": {"$mergeObjects": [
                        {"$arrayElemAt": ["$fromUsers", 0]}, "$$ROOT"]}}},
                    {"$project":
                     {
                         "fromUsers": 0,
                     }
                     },
                    {"$project":
                     {
                         "nickname": 1,
                         "num_orders": 1
                     }
                     },

                ])

            return pd.DataFrame(most_active_users_cursor)

        @st.cache
        def load_weekly_users():
            weekly_users = pd.read_csv(
                "resources/weekly_users.csv", skiprows=1)

            weekly_users.index = pd.to_datetime(weekly_users.Date)
            weekly_users = weekly_users.drop("Date", axis=1)

            weekly_users.columns = [get_country_alpha_3(
                c) for c in weekly_users.columns]
            return weekly_users

        # Users
        users = load_users()

        # Search for Specific User
        user_input = st.text_input("Insert User Nickname (Ex: rapxim)", "")

        if user_input:
            user = users[users.nickname == user_input]
            if user.empty:
                st.error(f'User {user_input} was not found')
            else:
                user = user.iloc[0]
                col1, col2 = st.columns([1, 4])
                col1.image(user.picture, use_column_width='always')
                col2.markdown(
                    f'Nickname: [{user.nickname}](https://www.faceit.com/en/players/{user.nickname})')
                col2.write(f'Coins: {user.coins}')
                col2.write(f'Member since: {user.createdAtDt}')

        # Most Active Users
        st.subheader("Most Active Users")
        most_active_users = get_most_active_users()

        fig = px.bar(
            data_frame=most_active_users,
            x='nickname',
            y="num_orders",
            title='Users with the highest number of Match Predictions',
            labels={"num_orders": "Number of Match Predictions",
                    "nickname": "User Nickname"})

        style_chart(fig, chart_type='bar')
        st.plotly_chart(fig, use_container_width=True)

        # Users Count Over Time
        st.subheader("Number of Users over time")

        fig = px.line(
            data_frame=users,
            x='createdAtDt',
            y="number_of_users",
            title='Number of total users over time',
            labels={"number_of_users": "Number of Users",
                    "createdAtDt": "Date"})

        style_chart(fig, chart_type='line')
        st.plotly_chart(fig, use_container_width=True)

        # Users Metrics
        for interval in ('months', 'days'):
            interval_name = interval[:-1]

            penultimate = get_users_metrics({interval: 2}, {interval: 1})
            latest = get_users_metrics({interval: 1}, {interval: 0})

            ratio_new_users = pct_change(
                latest["new_users"], penultimate["new_users"])
            ratio_active_users = pct_change(
                latest["active_users"], penultimate["active_users"])

            col1, col2 = st.columns(2)
            col1.metric(f"New users last {interval_name}",
                        latest["new_users"], f'{ratio_new_users:.1f}%')
            col2.metric(f"Active users last {interval_name}",
                        latest["active_users"], f'{ratio_active_users:.1f}%')

        draw_horizontal_line(st)

        # Users Count Over Time
        st.subheader("Weekly users geographical distribution")

        weekly_users = load_weekly_users()
        min_day = weekly_users.index.min().to_pydatetime()
        max_day = weekly_users.index.max().to_pydatetime()

        date_filter = st.slider(
            "Select date",
            min_value=min_day,
            max_value=max_day,
            value=min_day,
            format="ddd DD/MM/YY")

        weekly_users_day = weekly_users.loc[date_filter].to_dict()
        total_weekly_users = sum(weekly_users_day.values())

        colormap = [(0, "rgb(229, 236, 246)"), (0.2, "gray"),
                    (0.5, "#fe6300"), (1, "#f50")]
        fig = px.choropleth(locations=weekly_users_day.keys(),
                            color=weekly_users_day.values(),
                            color_continuous_scale=colormap,
                            title=f"Total weekly users: {total_weekly_users}",
                            labels={"color": "Users"})
        style_chart(fig, chart_type='map')
        st.plotly_chart(fig, use_container_width=True)
