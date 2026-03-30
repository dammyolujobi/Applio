import os 
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")

client = MongoClient(CONNECTION_STRING)
def get_db():
    return client["applio"]

db_name = get_db()

user_collection = db_name["user"]