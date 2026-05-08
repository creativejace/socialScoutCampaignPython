from core.base_client import BasePlatformClient
from .tiktok import TikTok
from .external import get_TikTok

class TikTokClient(BasePlatformClient):
    def __init__(self, platform: str):
        super().__init__(platform)

    def get_stats(self, post):
        try:
                # Implement TikTok-specific logic to get stats using the access token and video_id
                print(f"Fetching TikTok stats for video ID: {post['_id']} ")
                tiktok = TikTok(post['platform'])
                stats = tiktok.get_stats(post)
                return stats
        except Exception as e:
                print(f"Error fetching TikTok stats: {e}")
                print(f"Fallback to external api fetching TikTok stats for video ID: {post['_id']} ")
                get_TikTok(post)
                return None