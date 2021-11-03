from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.db import get_mongo_db
import streamlit as st


@st.experimental_memo(ttl=3600)
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


def pct_change(new_val, old_val):
    return 100*(new_val-old_val)/old_val
