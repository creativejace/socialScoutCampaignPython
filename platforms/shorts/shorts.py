from urllib.parse import urlparse

import requests
from typing import Dict

from services.token_service import get_access_token

BASE_URL = "https://graph.facebook.com/"


class Shorts:

    def __init__(self, platform: str):
        self.platform = platform
        self.provider = "google"

    def __get(self, post, access_token) -> Dict:

        url = post['link']
        parsed_url = urlparse(url)

        # The path attribute of the parsed URL will give '/reel/CyEhNnTyObD/'
        path_parts = parsed_url.path.split('/')
        reel_id = path_parts[2]  # This will give 'CyEhNnTyObD'


        url = f"{BASE_URL}{reel_id}/insights"
        params = {
            "metric": "impressions,reach,engagement,saved",
            "access_token": access_token
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_stats(self, post) -> Dict:
        try:
            token = get_access_token(post['platform'], post['_id'])
            data = self.__get(post, token)
            stats = {item['name']: item['values'][0]['value'] for item in data.get('data', [])}
            return stats
        except requests.RequestException as e:
            print(f"Error fetching Shorts stats: {e}")
            return {}