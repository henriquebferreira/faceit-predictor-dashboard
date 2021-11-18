from db.client import get_mongo_db
import pandas as pd
from dateutil.relativedelta import relativedelta
import streamlit as st
from datetime import datetime
from utils import timestamp_to_dt, get_country_alpha_3, object_id_to_dt
import pymongo
from utils import weekdays_map


@st.experimental_memo(ttl=3600)
def load_users():
    db = get_mongo_db()
    users = pd.DataFrame(db.users.find({}))
    users["createdAtDt"] = users._id.apply(object_id_to_dt)
    users = users.sort_values(by="createdAtDt", ascending=True)
    users["number_of_users"] = range(1, len(users)+1)
    users = users.drop(columns=["_id", "faceitId", "email"])
    return users


@ st.experimental_memo(ttl=3600)
def get_most_active_users(limit):
    db = get_mongo_db()
    most_active_users_cursor = db.orders.aggregate(
        [
            {"$group": {"_id": "$userId", "num_orders": {"$sum": 1}}},
            {"$sort": {"num_orders": -1}},
            {"$limit": limit},
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


@ st.cache
def load_weekly_users():
    weekly_users = pd.read_csv(
        "src/resources/weekly_users.csv", skiprows=1)

    weekly_users.index = pd.to_datetime(weekly_users.Date)
    weekly_users = weekly_users.drop("Date", axis=1)

    weekly_users.columns = [get_country_alpha_3(
        c) for c in weekly_users.columns]
    return weekly_users


@ st.experimental_memo(ttl=3600)
def get_users_metrics(min_interval, max_interval):
    db = get_mongo_db()
    now = datetime.today()
    min_ts = (now - relativedelta(**min_interval)).timestamp()
    max_ts = (now - relativedelta(**max_interval)).timestamp()

    num_new_users = db.users.find(
        {"createdAt": {"$gte": min_ts, "$lt": max_ts}}).count()

    active_users = db.orders.aggregate(
        [
            {"$match": {"timestamp": {"$gte": min_ts, "$lt": max_ts}}},
            {"$group": {"_id": "$userId"}},
            {"$group": {"_id": "", "count": {"$sum": 1}}},
            {"$project": {"_id": 0}},
        ])
    num_active_users = next(active_users)["count"]

    return {"new_users": num_new_users, "active_users": num_active_users}


@ st.experimental_memo(ttl=24*3600)
def load_orders(query_filter):
    db = get_mongo_db()
    orders = pd.DataFrame(db.orders.find(query_filter))
    orders = orders[orders.type == 'MATCH_PREDICT']

    orders["datetime"] = orders._id.apply(object_id_to_dt)
    orders = orders.sort_values(by="datetime", ascending=True)
    orders["hour"] = orders.datetime.apply(lambda x: x.hour)

    orders["day_of_week"] = orders.datetime.apply(
        lambda x: x.weekday())
    orders.day_of_week = orders.day_of_week.map(weekdays_map())

    orders["number_of_orders"] = range(1, len(orders)+1)
    orders = orders.drop(
        columns=["_id", "matchId", "type", "coinsBalance", "timestamp"], axis=1)

    return orders
