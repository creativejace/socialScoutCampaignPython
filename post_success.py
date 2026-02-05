from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os



def push_post(plays, likes, shares, comments, saves, post_id):
    # Connect to MongoDB
    load_dotenv(find_dotenv())
    password = os.environ.get("MONGODB_PWD")
    connection_string = f"mongodb+srv://creativechad:{password}@socialscout.u3xnrfr.mongodb.net/pointman?retryWrites=true&w=majority"
    client = MongoClient(connection_string)
    pointman_db = client.pointman
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

