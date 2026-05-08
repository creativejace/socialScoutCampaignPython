from time import timezone
from urllib.parse import urlparse
from datetime import datetime, timezone
from post_success import push_post_snapshots
import requests
from typing import Dict

from services.token_service import get_access_token

BASE_URL = "https://open.tiktokapis.com/v2/video/query/"


class TikTok:

    def __init__(self, platform: str):
        self.platform = platform
        self.provider = "tiktok"

    def __get(self, post, access_token) -> Dict:

        url = post['link']
        video_id = self.__get_tiktok_video_id(url)

        if not video_id:
            raise ValueError("Invalid TikTok URL")


        url = f"{BASE_URL}"
        # Adding fields as query parameters per TikTok API documentation
        params = {
            "fields": "like_count, comment_count, share_count, view_count" # Added extra useful fields
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # The data-raw part of your curl
        payload = {
            "filters": {
                "video_ids": [video_id]
            }
        }
        response = requests.post(url, params=params, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def __get_tiktok_video_id(self,url):
        path = urlparse(url).path.strip("/")
        parts = path.split("/")
        
        # Check for 'video' or 'v' in the path
        for pattern in ["video", "v"]:
            if pattern in parts:
                index = parts.index(pattern)
                if index + 1 < len(parts):
                    # .split('?')[0] ensures we drop query params if urlparse missed them
                    video_id = parts[index + 1].split('?')[0]
                    return video_id
        
        return None


    def get_stats(self, post) -> Dict:
        try:
            token = get_access_token(post['platform'], post['_id'])
            data = self.__get(post, token)
            stats = self.__parse_tiktok_video_list(data)
            print(f"✅ Fetched stats for TikTok post {post['_id']} from provider {self.provider} native api" )
            push_post_snapshots(stats, post['_id'])

            return stats
        except requests.RequestException as e:
            print(f"Error fetching TikTok stats: {e}")
            return {}
        
    def __parse_tiktok_video_list(self,api_response):
        """
        Parses the TikTok V2 API response and returns a list of dictionaries.
        Each dictionary contains stats for one video.
        """
        # 1. Error Handling: Check if the API status is 'ok'
        error_info = api_response.get("error", {})
        if error_info.get("code") != "ok":
            error_msg = error_info.get("message", "Unknown API Error")
            return {"error": f"API returned error: {error_msg}"}

        # 2. Access the video list
        video_data = api_response.get("data", {}).get("videos", [])
        
        if not video_data:
            return []

        # 3. Parse all videos into a list of objects
        parsed_list = [
            {
                "likes": v.get("like_count", 0),
                "views": v.get("view_count", 0),
                "shares": v.get("share_count", 0),
                "comments": v.get("comment_count", 0),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            for v in video_data
        ]
        
        return parsed_list