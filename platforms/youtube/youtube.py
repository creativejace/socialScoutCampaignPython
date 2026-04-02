import requests
from typing import Dict
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
from typing import List, Dict
from post_success import push_post, push_post_snapshots

BASE_URL = "https://youtubeanalytics.googleapis.com/v2/reports?"

#https://youtubeanalytics.googleapis.com/v2/reports?ids=channel==MINE&metrics=views,likes,comments&startDate=2024-01-01&endDate=2024-11-28&filters=video==9bbdPDiVx4Q&dimensions=day

class YouTube:

    def __init__(self, access_token: str):
        self.access_token = access_token

    def __get(self, post) -> Dict:

        url = post['link']
        video_id = _get_youtube_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        params = {
            "ids": "channel==MINE",
            "metrics": "views,likes,dislikes,comments,shares,estimatedMinutesWatched,subscribersGained,subscribersLost,averageViewDuration,averageViewPercentage,annotationImpressions,annotationCloseRate,annotationCloses,annotationClickableImpressions,annotationClickThroughRate,annotationClicks,cardImpressions,cardClickRate,cardClicks,cardTeaserImpressions,cardTeaserClickRate,cardTeaserClicks",
            "startDate": "2026-01-01",
            "endDate": "2026-02-04",
            "filters": f"video=={video_id}",
            "dimensions": "day"
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(BASE_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_stats(self, post) -> Dict:
        try:
            data = self.__get(post)
            stats = parseResponse(data)
            push_post_snapshots(stats, post['_id'])

            
            return stats
        except requests.RequestException as e:
            print(f"Error fetching YouTube stats: {e}")
            return {}

    from urllib.parse import urlparse, parse_qs

def _get_youtube_video_id(url: str) -> str | None:
    parsed = urlparse(url)

    # youtu.be/<id>
    if parsed.hostname in {"youtu.be"}:
        return parsed.path.lstrip("/")

    # youtube.com/*
    if parsed.hostname in {
        "www.youtube.com",
        "youtube.com",
        "m.youtube.com"
    }:
        # /watch?v=<id>
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]

        # /embed/<id> or /shorts/<id>
        if parsed.path.startswith(("/embed/", "/shorts/")):
            return parsed.path.split("/")[2]

    return None

def parseResponse(
    response: Dict,
) -> List[Dict]:
    headers = response.get("columnHeaders", [])
    rows = response.get("rows", [])

    # Separate headers
    dimensionHeaders = [
        h["name"] for h in headers if h["columnType"] == "DIMENSION"
    ]
    metricHeaders = [
        h["name"] for h in headers if h["columnType"] == "METRIC"
    ]

    snapshots = []

    metricHeaders.append("timestamp")
    metricHeaders.append("source")
    for row in rows:
        dimCount = len(dimensionHeaders)

        dimensionValues = row[:dimCount]
        metricValues = row[dimCount:]
        metricValues.append(datetime.now(timezone.utc).isoformat())
        metricValues.append("native")
        dimensions = dict(zip(dimensionHeaders, dimensionValues))
        snapshot = dict(zip(metricHeaders, metricValues))
        

        snapshots.append(snapshot)

    return snapshots