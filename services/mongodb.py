from pymongo import MongoClient
import os

client = None
db = None

def get_db():
    global client, db
    if client is None:
        username = os.getenv("MONGODB_USERNAME")
        password = os.getenv("MONGODB_PWD")
        database_name = os.getenv("MONGODB_DBNAME")
        connection_string = f"mongodb+srv://{username}:{password}@socialscout.u3xnrfr.mongodb.net/{database_name}?retryWrites=true&w=majority"
        client = MongoClient(connection_string)
        db = client[database_name]
    return db