from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os
from services.mongodb import get_db


def push_post_snapshots(snapshots, post_id):
    # Connect to MongoDB
    db = get_db()
    posts_collection = db.posts
    # The ID of the post you want to update
    post_id_obj = ObjectId(post_id) 

    for snapshot in snapshots:   
        # Update the post to add the new snapshots
        posts_collection.update_one(
            {"_id": post_id_obj},
            {"$push": {"snapshot": snapshot}}
        )

    print("Snapshot added!")



def push_post(plays, likes, shares, comments, saves, post_id):
    # Connect to MongoDB
    load_dotenv(find_dotenv())
    password = os.environ.get("MONGODB_PWD")
    connection_string = f"mongodb+srv://hiteshguptacipl_db_user:{password}@socialscout.u3xnrfr.mongodb.net/mydb?retryWrites=true&w=majority"
    client = MongoClient(connection_string)
    pointman_db = client.crypsis
    posts_collection = pointman_db.posts
    # The ID of the post you want to update
    post_id_obj = ObjectId(post_id)  # Replace with the actual post ID you want to update

    # Define the snapshot object you want to add
    new_snapshot = {
        "views": plays,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "timestamp": datetime.now()
    }

    # Update the post to add the new snapshot
    posts_collection.update_one(
        {"_id": post_id_obj},
        {"$push": {"snapshot": new_snapshot}}
    )

    print("Snapshot added!")

def push_India_post(plays, likes, shares, comments, saves, post_id):
    # Connect to MongoDB
    # load_dotenv(find_dotenv())
    password = os.environ.get("MONGODB_PWD")
    connection_string = f"mongodb+srv://hiteshguptacipl_db_user:{password}@socialscout.u3xnrfr.mongodb.net/mydb?retryWrites=true&w=majority"
    client = MongoClient(connection_string)
    mydb = client.mydb
    posts_collection = mydb.posts
    # The ID of the post you want to update
    post_id_obj = ObjectId(post_id)  # Replace with the actual post ID you want to update

    # Define the snapshot object you want to add
    new_snapshot = {
        "views": plays,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "timestamp": datetime.now()
    }

    # Update the post to add the new snapshot
    posts_collection.update_one(
        {"_id": post_id_obj},
        {"$push": {"snapshot": new_snapshot}}
    )

    print("Snapshot added!")