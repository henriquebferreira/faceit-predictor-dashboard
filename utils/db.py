
from pymongo import MongoClient

def get_mongo_db(st):
    mongo_secrets = st.secrets["mongo"]
    username = mongo_secrets["username"]
    password = mongo_secrets["password"]
    srv_connection = mongo_secrets["srv_connection"]

    connection_string = f"mongodb+srv://{username}:{password}@{srv_connection}"
    client = MongoClient(connection_string)
    db = client['faceit-predictor']

    return db