from core.base_client import BasePlatformClient
from .instagram import Instagram
from .external import get_Instagram

class InstagramClient(BasePlatformClient):
    def __init__(self, access_token):
        super().__init__(access_token)

    def get_stats(self, post):
        #try:
            # Implement Instagram-specific logic to get stats using the access token and video_id
        #    print(f"Fetching Instagram stats for video ID: {post['_id']} ")
            
        #    return stats
        #except Exception as e:
        #    print(f"Error fetching Instagram stats: {e}")
           get_Instagram(post)
        #    return None