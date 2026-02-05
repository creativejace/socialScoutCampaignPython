from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
from posts import get_posts
from campaign_fetcher import get_campaign_with_latest_snapshot
import json
from bson.objectid import ObjectId

# Load environment variables
load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")

# MongoDB connection setup
connection_string = f"mongodb+srv://creativechad:{password}@socialscout.u3xnrfr.mongodb.net/pointman?retryWrites=true&w=majority"
client = MongoClient(connection_string)
pointman_db = client.pointman
campaigns_collection = pointman_db.campaigns

# Utility: Fetch campaign by ID
def get_campaign_by_id(campaign_id):
    _id = ObjectId(campaign_id)
    return campaigns_collection.find_one({"_id": _id})

# ✅ Lambda Handler — Single Campaign Only
def lambda_handler(event, context):
    try:
        # Parse the incoming event
        body = json.loads(event["body"]) if "body" in event and event["body"] else {}

        campaign_id = body.get("campaign_id") if body else None

        if not campaign_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps("Missing campaign_id in request.")
            }

        print(f"Fetching campaign with ID: {campaign_id}")
        campaign = get_campaign_by_id(campaign_id)

        if not campaign:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps(f"No campaign found for ID: {campaign_id}")
            }

        run_id = str(campaign["_id"])
        print(f"Processing campaign with run_id: {run_id}")
        campaign_details = get_campaign_with_latest_snapshot(run_id, campaigns_collection)
        print("Campaign details fetched successfully.")

        for post in campaign_details["post_details"]:
            print(f"Processing post: {post}")
            get_posts(post)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps("Campaign processing complete.")
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps(f"Internal Server Error: {str(e)}")
        }

# ✅ Local test block for PyCharm or development use only
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "campaign_id": "6750d3822c0d7cb6e6de7ee8"  # Replace with your test ID
        })
    }

    response = lambda_handler(test_event, None)
    print("Local execution response:", response)