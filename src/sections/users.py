import plotly.express as px
from utils import style_chart
from components.horizontal_line import draw_horizontal_line
from utils import pct_change
from sections.base_section import Section
from db.loaders import get_most_active_users, load_users, load_weekly_users, get_users_metrics
import streamlit as st


class UsersSection(Section):
    def __init__(self):
        super(UsersSection, self).__init__("Users")

    def core_draw(self):
        users = load_users()

        # Search for Specific User
        user_input = st.text_input("Insert User Nickname (Ex: rapxim)", "")

        if user_input:
            user = users[users.nickname == user_input]
            if user.empty:
                st.error(f'User {user_input} was not found')
            else:
                user = user.iloc[0]
                # TODO: build custom user component
                col1, col2 = st.columns([1, 4])
                col1.image(user.picture, use_column_width='always')
                col2.markdown(
                    f'Nickname: [{user.nickname}](https://www.faceit.com/en/players/{user.nickname})')
                col2.write(f'Coins: {user.coins}')
                col2.write(f'Member since: {user.createdAtDt}')

        # Most Active Users
        st.subheader("Most Active Users")
        most_active_users = get_most_active_users(limit=15)

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

        draw_horizontal_line()

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

        fig = px.choropleth(locations=weekly_users_day.keys(),
                            color=weekly_users_day.values(),
                            title=f"Total weekly users: {total_weekly_users}",
                            labels={"color": "Users"})
        style_chart(fig, chart_type='map')
        st.plotly_chart(fig, use_container_width=True)
