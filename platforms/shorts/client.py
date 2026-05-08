from core.base_client import BasePlatformClient
from .shorts import Shorts
from .external import get_shorts

class ShortsClient(BasePlatformClient):
    def __init__(self, access_token):
        super().__init__(access_token)

    def get_stats(self, post):
        #try:
            # Implement Shorts-specific logic to get stats using the access token and video_id
        #    print(f"Fetching Shorts stats for video ID: {post['_id']} ")
        #    stats = get_stats(post)
        #    return stats
        #except Exception as e:
        #    print(f"Error fetching Shorts stats: {e}")
            get_shorts(post)
        #    return None