from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
from posts import get_posts
from campaign_fetcher import get_campaign_with_latest_snapshot
import json
from bson.objectid import ObjectId
from tiktok import get_TikTok
from instagram import get_Instagram
from youtube import get_youtube
from services.token_service import get_access_token
from core.registry import get_platform_client
from campaign_fetcher import get_campaign_with_latest_snapshot
from bson.objectid import ObjectId
from posts import get_posts2

# Load environment variables
load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")
# MongoDB connection setup
connection_string = f"mongodb+srv://hiteshguptacipl_db_user:{password}@socialscout.u3xnrfr.mongodb.net/pointman?retryWrites=true&w=majority"
client = MongoClient(connection_string)
pointman_db = client.crypsis
campaigns_collection = pointman_db.campaigns

def get_campaign_by_id(campaign_id):
    _id = ObjectId(campaign_id)
    return campaigns_collection.find_one({"_id": _id})
# ✅ Lambda Handler — Single Campaign Only
def lambda_handler(event, context):
    try:
        # Parse the incoming event
        body = json.loads(event["body"]) if "body" in event and event["body"] else {}

        # campaign_id = body.get("run_id") if body else None
       
       
        run_id = body.get("campaign_id")  # Replace with actual campaign ID or run ID
        if not run_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps("Missing campaign_id in request.")
            }
        print(f"Processing campaign with run_id: {run_id}")
        campaign = get_campaign_by_id(run_id)
        if not campaign:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps(f"No campaign found for ID: {run_id}")
            }

        campaign_details = get_campaign_with_latest_snapshot(run_id, campaigns_collection)
        if not campaign_details:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps(f"No campaign found for ID: {run_id}")
            }

        print("Campaign details fetched successfully.")

        for post in campaign_details["post_details"]:
            print(f"Processing post: {post}")
            get_posts2(post)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps("Campaign processing complete.")
        }
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "❌ Invalid JSON format in request body"})
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

