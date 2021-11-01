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

    intervals = [{"months": 1}, {"days": 1}]
    for i in intervals:
        before_date = datetime.today() - relativedelta(**i)
        before_timestamp = before_date.timestamp()

        num_new_users = len(users[users.createdAt >= before_timestamp])

        active_users = orders_coll.aggregate(
            [
                {"$match": {"timestamp": {"$gt": before_timestamp}}},
                {"$group": {"_id": "$userId"}},
                {"$group": {"_id": "", "count": {"$sum": 1}}},
                {"$project": {"_id": 0}},
            ])
        num_active_users = list(active_users)[0]["count"]

        interval_name = list(i.keys())[0][:-1]
        col1, col2 = st.columns(2)
        col1.metric(f"New users last {interval_name}", num_new_users)
        col2.metric(f"Active users last {interval_name}", num_active_users)

    draw_horizontal_line(st)