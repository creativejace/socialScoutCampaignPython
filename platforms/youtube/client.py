from core.base_client import BasePlatformClient
from .youtube import YouTube
from .external import get_youtube

class YouTubeClient(BasePlatformClient):
    def __init__(self, platform: str):
        super().__init__(platform)

    def get_stats(self, post):
        try:
            # Implement YouTube-specific logic to get stats using the access token and video_id
            print(f"Fetching YouTube stats for video ID: {post['_id']} ")
            youtube = YouTube(post['platform'])
            stats = youtube.get_stats(post)
            return stats
        except Exception as e:
            print(f"Error fetching YouTube stats: {e}")
            print(f"Fallback to external api fetching YouTube stats for video ID: {post['_id']} ")
            get_youtube(post)
            return None