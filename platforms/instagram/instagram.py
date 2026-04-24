from datetime import datetime, timedelta, timezone
import os
import requests
from typing import Dict
from bson.objectid import ObjectId

from services.token_service import get_access_token
from services.mongodb import get_db

BASE_URL = "https://graph.facebook.com/v25.0"


class Instagram:
    def __init__(self, platform: str):
        self.platform = platform
        self.provider = "facebook"


    def _get_saved_media_id(self, post_id):
        db = get_db()
        posts_collection = db.posts
        post_id_obj = post_id if isinstance(post_id, ObjectId) else ObjectId(post_id)

        post_doc = posts_collection.find_one(
            {"_id": post_id_obj},
            {"instagram_media_id": 1}
        )

        if post_doc:
            return post_doc.get("instagram_media_id")
        return None

    def _save_media_id(self, post_id, media_id):
        db = get_db()
        posts_collection = db.posts
        post_id_obj = post_id if isinstance(post_id, ObjectId) else ObjectId(post_id)

        result = posts_collection.update_one(
            {"_id": post_id_obj},
            {"$set": {"instagram_media_id": media_id}}
        )

        print(f"✅ instagram_media_id saved in DB. Matched={result.matched_count}, Modified={result.modified_count}")

    def _get_or_create_media_id(self, post) -> str:
        post_id = post["_id"]
        db = get_db()
        posts_collection = db.posts
        fresh_post = posts_collection.find_one({"_id": post_id})

        instagram_media_id = fresh_post.get("instagram_media_id")

        if instagram_media_id:
            print(f"✅ Using existing instagram_media_id from DB: {instagram_media_id}")
            return instagram_media_id

        # app under review, so use testing media id
        else:
            media_id = "18007846955850770"
            print(f"⚠️ instagram_media_id not found in DB, using testing media_id: {media_id}")

            self._save_media_id(post_id, media_id)
            return media_id

    def _get_instagram_insights(self, media_id: str, access_token: str) -> Dict:
        url = f"{BASE_URL}/{media_id}/insights"
        params = {
            "metric": "reach,saved,likes,comments,shares,ig_reels_video_view_total_time,ig_reels_avg_watch_time,views,reels_skip_rate,reposts",
            "period": "day",
            "access_token": access_token
        }

        response = requests.get(url, params=params, timeout=30)
        print("🔵 Instagram insights status:", response.status_code)
        print("🔵 Instagram insights response:", response.text)
        response.raise_for_status()

        return response.json()

    def _convert_insights_to_stats(self, insights_data: Dict) -> Dict:
        stats = {}

        for item in insights_data.get("data", []):
            name = item.get("name")
            values = item.get("values", [])

            if values and isinstance(values, list):
                stats[name] = values[0].get("value", 0)
            else:
                stats[name] = 0

        return stats

    def _save_snapshot(self, post_id, final_stats: Dict):
        db = get_db()
        posts_collection = db.posts
        post_id_obj = post_id if isinstance(post_id, ObjectId) else ObjectId(post_id)

        snapshot_data = {
            "views": final_stats.get("views", 0),
            "likes": final_stats.get("likes", 0),
            "comments": final_stats.get("comments", 0),
            "shares": final_stats.get("shares", 0),
            "saves": final_stats.get("saved", 0),
            "reach": final_stats.get("reach", 0),
            "saved": final_stats.get("saved", 0),
            "ig_reels_video_view_total_time": final_stats.get("ig_reels_video_view_total_time", 0),
            "ig_reels_avg_watch_time": final_stats.get("ig_reels_avg_watch_time", 0),
            "reels_skip_rate": final_stats.get("reels_skip_rate", 0),
            "reposts": final_stats.get("reposts", 0),
            "timestamp": datetime.now(timezone.utc)
        }

        result = posts_collection.update_one(
            {"_id": post_id_obj},
            {"$push": {"snapshot": snapshot_data}}
        )

        print(f"✅ Snapshot saved in DB. Matched={result.matched_count}, Modified={result.modified_count}")
        print("✅ Snapshot data:", snapshot_data)

    def get_stats(self, post) -> Dict:
        try:
            access_token = get_access_token(self.provider, post["_id"])
            # print(f"✅ Current Facebook access token received: {access_token}")   



            media_id = self._get_or_create_media_id(post)
            print(f"✅ Final media_id: {media_id}")

            insights_response = self._get_instagram_insights(media_id, access_token)
            final_stats = self._convert_insights_to_stats(insights_response)

            print("✅ Final Instagram reel insight stats:", final_stats)

            # save in snapshot array
            self._save_snapshot(post["_id"], final_stats)

            return final_stats

        except requests.RequestException as e:
            print(f"Error fetching Instagram insights: {e}")
            raise
        except Exception as e:
            print(f"Error in Instagram native method: {e}")
            raise