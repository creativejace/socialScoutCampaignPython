import datetime
import os
from datetime import timezone

from core.exceptions import ApiException
from .mongodb import get_db
from bson.objectid import ObjectId
import requests

def get_access_token(provider,post_id):
    token = _get_token(provider,post_id)
    print("provider:", provider)
    print("token:", token)
    if token:
        if token['user']['token']['provider'] == provider:
            
            if provider == "facebook":
                refreshTokenExpiresAt = token['user']['token']['expiresAt']
                refresh_token = token['user']['token']['accessToken']
                access_token = _get_facebook_access_token(token['user']['token'])
                token_id = token['user']['token']['_id']
                new_access_token = _refresh_facebook_token(token_id,access_token)
                print("✅ Refreshed Facebook token received")
                return new_access_token
            lastRefreshedAt = token['user']['token']['lastRefreshedAt']
            refreshTokenExpiresIn = token['user']['token']['refreshTokenExpiresIn']
            
            refreshTokenExpiresAt = lastRefreshedAt + datetime.timedelta(seconds=refreshTokenExpiresIn)
            refresh_token = token['user']['token']['refreshToken']

            print(f"✅ Refresh Token Expires At: {refreshTokenExpiresAt}")
            if provider == "google":
                token_id = token['user']['token']['_id']
                access_token = _get_google_access_token(token_id, refresh_token)
                return access_token
            elif provider == "tiktok":
                token_id = token['user']['token']['_id']
                access_token = _get_tiktok_access_token(token_id, refresh_token)
                return access_token
    return None

def _get_google_access_token(token_id, refresh_token):
    url = "https://oauth2.googleapis.com/token"

    payload = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data=payload, timeout=30)
    print("🔵 Google refresh status:", response.status_code)
    # print("🔵 Google refresh response:", response.text)
    response.raise_for_status()

    if not 200 <= response.status_code < 300:
        raise ApiException(
            statusCode=response.status_code,
            message=f"HTTP call failed with status {response.status_code}",
            responseBody=response.text,
        )

    token_data = response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise ValueError(f"access_token not found in refresh response: {token_data}")

    _update_google_token_in_db(token_id, token_data)

    return access_token

def _update_google_token_in_db(token_id, token_data: dict):
        db = get_db()
        tokens_collection = db.tokens

        now = datetime.datetime.now(timezone.utc)

        update_fields = {
            "accessToken": token_data.get("access_token"),
            "lastRefreshedAt": now,
            "updatedAt": now,
            "scope": token_data.get("scope"),
            "tokenType": token_data.get("token_type"),
        }

        if token_data.get("expires_in"):
            update_fields["expiresAt"] = int(now.timestamp()) + int(token_data.get("expires_in"))

        if token_data.get("id_token"):
            update_fields["idToken"] = token_data.get("id_token")

        result = tokens_collection.update_one(
            {"_id": token_id, "provider": "google"},
            {"$set": update_fields}
        )

        print(f"✅ Google token updated in DB. Matched={result.matched_count}, Modified={result.modified_count}")
def _get_tiktok_access_token(token_id, refresh_token):
    url = "https://open.tiktokapis.com/v2/oauth/token/"

    payload = {
        "client_key": os.getenv("TIKTOK_CLIENT_ID"),
        "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data=payload, timeout=30)
    print("🔵 TikTok refresh status:", response.status_code)
    # print("🔵 TikTok refresh response:", response.text)
    response.raise_for_status()

    if not 200 <= response.status_code < 300:
        raise ApiException(
            statusCode=response.status_code,
            message=f"HTTP call failed with status {response.status_code}",
            responseBody=response.text,
        )

    token_data = response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise ValueError(f"access_token not found in refresh response: {token_data}")

    _update_tiktok_token_in_db(token_id, token_data)

    return access_token
def _update_tiktok_token_in_db(token_id, token_data: dict):
        db = get_db()
        tokens_collection = db.tokens

        now = datetime.datetime.now(timezone.utc)

        update_fields = {
            "accessToken": token_data.get("access_token"),
            "lastRefreshedAt": now,
            "updatedAt": now,
            "scope": token_data.get("scope"),
            "refreshToken": token_data.get("refresh_token"),
            "providerAccountId": token_data.get("open_id"),
            "tokenType": token_data.get("token_type"),
            "expiresAt": int(now.timestamp()) + int(token_data.get("expires_in")),
            "refreshTokenExpiresIn":int(token_data.get("refresh_expires_in")),
        }


        result = tokens_collection.update_one(
            {"_id": token_id, "provider": "tiktok"},
            {"$set": update_fields}
        )

        print(f"✅ TikTok token updated in DB. Matched={result.matched_count}, Modified={result.modified_count}")

def _get_facebook_access_token(token_data):
    access_token = token_data.get("accessToken")
    if not access_token:
        raise ApiException(
            statusCode=400,
            message="Facebook access token not found",
            responseBody=str(token_data),
        )
    return access_token
def _refresh_facebook_token(token_id, current_access_token: str):
        url = "https://graph.facebook.com/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": os.getenv("FACEBOOK_CLIENT_ID"),
            "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET"),
            "fb_exchange_token": current_access_token,
        }

        response = requests.get(url, params=params, timeout=30)
        print("🔵 Facebook refresh status:", response.status_code)
        # print("🔵 Facebook refresh response:", response.text)
        response.raise_for_status()

        data = response.json()
        new_access_token = data.get("access_token")
        expires_in = data.get("expires_in")

        if not new_access_token:
            raise ValueError(f"access_token not found in refresh response: {data}")

        _update_facebook_token_in_db(token_id, new_access_token, expires_in)
        print("✅ Facebook token refreshed and updated in DB inside the referesh function")

        return new_access_token
def _update_facebook_token_in_db(token_id, new_access_token: str, expires_in: int):
        db = get_db()
        tokens_collection = db.tokens

        now = datetime.datetime.now(timezone.utc)

        update_fields = {
            "accessToken": new_access_token,
            "lastRefreshedAt": now,
            "updatedAt": now,
        }

        if expires_in:
            update_fields["expiresAt"] = update_fields["expiresAt"] = int(now.timestamp()) + int(expires_in)

        result = tokens_collection.update_one(
            {"_id": token_id, "provider": "facebook"},
            {"$set": update_fields}
        )

        print(f"✅ Facebook token updated in DB. Matched={result.matched_count}, Modified={result.modified_count}")
    
def _get_token(provider, post_id):
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
            "user.token.provider": provider
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
    print("aggregation result:", result)
    return result[0] if result else None  # Return single document if available

