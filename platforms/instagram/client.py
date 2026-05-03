from core.base_client import BasePlatformClient
from .instagram import Instagram
from .external import get_Instagram

class InstagramClient(BasePlatformClient):
    def __init__(self, platform: str):
        super().__init__(platform)
        self.instagram_api = Instagram(platform)

    def get_stats(self, post):
        try:
            print(f"🔵 Trying native Instagram method...Post_id: {post['_id']}")
            stats = self.instagram_api.get_stats(post)
            print(f"✅ Native Instagram method worked Post_id: {post['_id']}")
            return stats
        except Exception as e:
            print(f"❌ Native Instagram method failed: {e}")
            print("➡ Switching to fallback method...")
            return get_Instagram(post)