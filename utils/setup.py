import os 
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING", "mongodb://localhost:27017")

client = MongoClient(CONNECTION_STRING)
def get_db():
    return client["applio"]

db_name = get_db()

user_collection = db_name["users"]
job_cache_collection = db_name["job_cache"]
saved_jobs_collection = db_name["saved_jobs"]
job_alerts_collection = db_name["job_alerts"]
applications_collection = db_name["applications"]
search_history_collection = db_name["search_history"]
user_activity_collection = db_name["user_activity"]
admin_stats_collection = db_name["admin_stats"]