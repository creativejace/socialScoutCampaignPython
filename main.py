from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
import json
from bson.objectid import ObjectId

from campaign_fetcher import get_campaign_with_latest_snapshot
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
        # Parse request body safely
        body = json.loads(event["body"]) if "body" in event and event["body"] else {}

        run_id = body.get("campaign_id")

        # ✅ Missing validation (added)
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

        print(f"Fetching campaign with ID: {run_id}")

        # ✅ Check campaign exists (added)
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

        print(f"Processing campaign with run_id: {run_id}")

        # ✅ Fetch campaign details
        campaign_details = get_campaign_with_latest_snapshot(run_id, campaigns_collection)

        # ✅ Missing check (added)
        if not campaign_details:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps(f"No campaign details found for ID: {run_id}")
            }

        print("Campaign details fetched successfully.")

        # ✅ Safe access (important fix)
        post_list = campaign_details.get("post_details", [])

        if not post_list:
            print("⚠️ No posts found in campaign")
            return {
                "statusCode": 200,
                "body": json.dumps("No posts to process.")
            }

        # ✅ Process posts
        for post in post_list:
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


# ✅ Local Test
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "campaign_id": "651c58a0c7cdede479ad539e"
        })
    }

    response = lambda_handler(test_event, None)
    print("Lambda Response:", response)