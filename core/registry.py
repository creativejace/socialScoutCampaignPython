from platforms.instagram.client import InstagramClient
from platforms.tiktok.client import TikTokClient
from platforms.shorts.client import ShortsClient
from platforms.youtube.client import YouTubeClient

PLATFORM_REGISTRY = {
    'instagram': InstagramClient,
    'tiktok': TikTokClient,
    'shorts': ShortsClient,
    'youtube': YouTubeClient,
} 
def get_platform_client(platform):
    client_class = PLATFORM_REGISTRY.get(platform.lower())
    if not client_class:
        raise ValueError(f"Unsupported platform: {platform}")
    return client_class(platform)