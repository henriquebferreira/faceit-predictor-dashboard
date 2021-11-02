# subfig = make_subplots(specs=[[{"secondary_y": True}]])

# # create two independent figures with px.line each containing data from multiple columns
# fig = px.line(data_frame=sorted_users_by_account_age,
#               x='createdAtDatetime',
#               y="number_of_users")
# fig2 = px.line(data_frame=sorted_orders_by_timestamp,
#                x='datetime',
#                y="number_of_orders")

# fig2.update_traces(yaxis="y2")
# subfig.add_traces(fig.data + fig2.data)
# subfig.layout.xaxis.title = "Date"
# subfig.layout.yaxis.title = "Number of Users"
# subfig.layout.yaxis2.title = "Number of Orders"
# # subfig.for_each_trace(lambda t: t.update(line=dict(color=colors[1])))
# style_chart(subfig, chart_type='bar')
# st.plotly_chart(subfig, use_container_width=True)
import pandas as pd
from datetime import datetime
import pycountry
from dateutil.relativedelta import relativedelta
import plotly.express as px
from utils.style import style_chart
from utils.elements import draw_horizontal_line


def draw_users(st, db):
    matches_coll = db.matches
    features_coll = db.features
    orders_coll = db.orders
    users_coll = db.users

    @st.experimental_memo(ttl=24*3600)
    def load_users():
        return list(users_coll.find({}))

    # Users
    st.header("Users")
    users = pd.DataFrame(load_users())

    # User example
    user_input = st.text_input("Insert User Nickname", "")

    if not user_input:
        st.markdown("Sample User")
        selected_user = users[users.nickname == 'rapxim']
    else:
        selected_user = users[users.nickname == user_input]

    if selected_user.empty:
        st.error(f'User {user_input} was not found')
    else:
        selected_user = selected_user.iloc[0]
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(selected_user.picture, use_column_width='always')
            with col2:
                link = f'Nickname: [{selected_user.nickname}](https://www.faceit.com/en/players/{selected_user.nickname})'
                st.markdown(link, unsafe_allow_html=True)
                st.write(f'Coins: {selected_user.coins}')
                st.write(
                    f'Member since: {datetime.fromtimestamp(selected_user.createdAt)}')

    # most active users
    st.subheader("Most Active Users")
    most_active_users_cursor = orders_coll.aggregate(
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

    most_active_users = pd.DataFrame(most_active_users_cursor)

    fig = px.bar(
        data_frame=most_active_users,
        x='nickname',
        y="num_orders",
        title='Users with the highest number of Match Predictions',
        labels={
            "num_orders": "Number of Match Predictions",
            "nickname": "User Nickname"},
    )
    style_chart(fig, chart_type='bar')
    st.plotly_chart(fig, use_container_width=True)

    # users over time
    st.subheader("Number of Users over time")
    users["createdAtDt"] = users.createdAt.apply(
        lambda x: datetime.fromtimestamp(x))
    users = users.sort_values(by="createdAtDt")
    users["number_of_users"] = range(1, len(users)+1)

    fig = px.line(
        data_frame=users,
        x='createdAtDt',
        y="number_of_users",
        title='Number of total users over time',
        labels={
            "number_of_users": "Number of Users",
            "createdAtDt": "Date"},
    )
    style_chart(fig, chart_type='line')
    st.plotly_chart(fig, use_container_width=True)
    
    intervals = [
        {"min":dict(months=2), "max":{"months": 1}},
        {"min":{"months": 1}, "max":{"months": 0}},
        {"min":{"days": 2}, "max":{"days": 1}},
        {"min":{"days": 1}, "max":{"days": 0}}
        ]

    
    
    def get_new_and_active_users(min_interval, max_interval):
        min_date = datetime.today() - relativedelta(**min_interval)
        min_timestamp = min_date.timestamp()

        max_date = datetime.today() - relativedelta(**max_interval)
        max_timestamp = max_date.timestamp()

        num_new_users = len(users[(users.createdAt >= min_timestamp)
         & (users.createdAt < max_timestamp)])

        active_users = orders_coll.aggregate(
            [
                {"$match": {"timestamp": {"$gte": min_timestamp, "$lt": max_timestamp}}},
                {"$group": {"_id": "$userId"}},
                {"$group": {"_id": "", "count": {"$sum": 1}}},
                {"$project": {"_id": 0}},
            ])
        num_active_users = list(active_users)[0]["count"]

        return {"new_users":num_new_users, "active_users":num_active_users}

    for interval_name in ('months', 'days'):
        two_months = get_new_and_active_users({interval_name:2}, {interval_name:1})
        last_month = get_new_and_active_users({interval_name:1}, {interval_name:0})

        ratio_new_users = 100*(last_month["new_users"]-two_months["new_users"])/two_months["new_users"]
        ratio_active_users = 100*(last_month["active_users"]-two_months["active_users"])/two_months["active_users"]

        col1, col2 = st.columns(2)
        col1.metric(f"New users last {interval_name[:-1]}",
                    last_month["new_users"],
                    f'{ratio_new_users:.1f}%')
        col2.metric(f"Active users last {interval_name[:-1]}",
                    last_month["active_users"],
                    f'{ratio_active_users:.1f}%')


    st.subheader("Weekly users geographical distribution")

    @st.cache(allow_output_mutation=True)
    def load_weekly_users():
        return pd.read_csv("weekly_users.csv", skiprows=1)

    weekly_users = load_weekly_users()

    weekly_users.index = weekly_users.Date
    weekly_users = weekly_users.drop("Date", axis=1)

    min_day = datetime.strptime(weekly_users.index.min(), "%Y-%m-%d")
    max_day = datetime.strptime(weekly_users.index.max(), "%Y-%m-%d")

    start_time = st.slider(
        "Filter Weekly Users Data by Day",
        min_value=min_day,
        max_value=max_day,
        value=min_day,
        format="ddd DD/MM/YY")

    def get_country_alpha_3(country_name):
        if country_name == 'XK':
            country_name = 'Kosovo'
        elif country_name == 'UAE':
            country_name= 'United Arab Emirates'
        close_countries = pycountry.countries.search_fuzzy(country_name)
        return close_countries[0].alpha_3
        
    weekly_users.columns = [get_country_alpha_3(c) for c in weekly_users.columns]
    
    data = weekly_users.loc[start_time.strftime("%Y-%m-%d")].to_dict()

    total_weekly_users = sum(data.values())

    fig = px.choropleth(locations=data.keys(),
                        color=data.values(),
                        # color_continuous_scale=px.colors.sequential.Sunset,
                        color_continuous_scale=[(0,"rgb(229, 236, 246)"), (0.2, "gray"), (0.5, "#fe6300"), (1, "#f50")],
                        title=f"Total weekly users: {total_weekly_users}",
                        labels={"color": "Users"})
    # style_chart(fig, chart_type='bar')
    fig.update_geos(bgcolor= 'rgb(51, 51, 51)')
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=40))
    st.plotly_chart(fig, use_container_width=True)
    draw_horizontal_line(st)