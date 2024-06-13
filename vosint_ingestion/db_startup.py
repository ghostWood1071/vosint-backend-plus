from vosint_ingestion.models.mongorepository import MongoRepository
from pymongo import ASCENDING, DESCENDING, TEXT 

def init_index():
    mongo_db = MongoRepository()
    mongo_db.create_index("News", "created_at", ASCENDING)
    mongo_db.create_index("events", "created_at", ASCENDING)
    mongo_db.create_index("his_log", "created_at", ASCENDING)
    mongo_db.create_index("queue", "expire", ASCENDING, {"expireAfterSeconds": 43200})
    mongo_db.create_index("queue", "url", ASCENDING, {"unique": True})
    mongo_db.create_index("report", "title", TEXT)