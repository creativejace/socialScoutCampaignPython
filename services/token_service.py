import os

from core.exceptions import ApiException
from .mongodb import get_db
from bson.objectid import ObjectId
import requests

def get_access_token(platform_name,post_id):
    token = _get_token(platform_name,post_id)
    if token:
        if token['user']['token']['provider'] == 'google':
            refresh_token = token['user']['token']['refreshToken']
            access_token = _get_google_access_token(refresh_token)
            print(f"✅ Access token retrieved" )
            return access_token
    return None

def _get_google_access_token(refresh_token):
    url = "https://oauth2.googleapis.com/token"

    payload = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data=payload)
    response.raise_for_status()

    # Explicitly handle non-2xx responses
    if not 200 <= response.status_code < 300:
        raise ApiException(
            statusCode=response.status_code,
            message=f"HTTP call failed with status {response.status_code}",
            responseBody=response.text,
        )

    data = response.json()
    return data["access_token"]

def _get_token(platform_name, post_id):
    db = get_db()
    posts_collection = db.posts
    _id = ObjectId(post_id)

    pipeline = [
    {
        "$match":
        {
            "_id": _id
        }
    },
    {
        "$lookup":
        {
            "from": "users",
            "localField": "creator",
            "foreignField": "creator",
            "as": "user"
        }
    },
    {
        "$unwind":
        {
            "path": "$user",
            "preserveNullAndEmptyArrays": True
        }
    },
    {
        "$lookup":
        {
            "from": "tokens",
            "localField": "user._id",
            "foreignField": "userId",
            "as": "user.token"
        }
    },
    {
        "$unwind":
        {
            "path": "$user.token",
            "preserveNullAndEmptyArrays": True
        }
    },
    {
        "$match":
        {
            "user.token.provider": "google"
        }
    },
    {
        "$project":
        {
            "user.token": 1
        }
    }
]
    result = list(posts_collection.aggregate(pipeline))
    return result[0] if result else None  # Return single document if available