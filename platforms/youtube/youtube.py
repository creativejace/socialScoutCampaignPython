from urllib import response

import requests
from typing import Dict
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
from typing import List, Dict
from post_success import push_post, push_post_snapshots
from services.token_service import ApiException, get_access_token
from urllib.parse import urlparse, parse_qs

BASE_URL = "https://youtubeanalytics.googleapis.com/v2/reports?"

#https://youtubeanalytics.googleapis.com/v2/reports?ids=channel==MINE&metrics=views,likes,comments&startDate=2024-01-01&endDate=2024-11-28&filters=video==9bbdPDiVx4Q&dimensions=day

class YouTube:

    def __init__(self, platform: str):
        self.platform = platform
        self.provider = "google"

    def __get(self, post,access_token) -> Dict:

        url = post['link']
        video_id = self.__get_youtube_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        todayUtc = datetime.now(timezone.utc).date().isoformat()

        params = {
            "ids": "channel==MINE",
            "metrics": "views,likes,dislikes,comments,shares,estimatedMinutesWatched,subscribersGained,subscribersLost,averageViewDuration,averageViewPercentage,annotationImpressions,annotationCloseRate,annotationCloses,annotationClickableImpressions,annotationClickThroughRate,annotationClicks,cardImpressions,cardClickRate,cardClicks,cardTeaserImpressions,cardTeaserClickRate,cardTeaserClicks",
            "startDate": "2020-01-01", # just a very old date to ensure we get all data for the video
            "endDate": todayUtc,
            "filters": f"video=={video_id}",
            #"dimensions": "day"
        }
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(BASE_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_stats(self, post) -> Dict:

        token = get_access_token(self.provider, post['_id'])
        if token is None:
            raise  ApiException(
                statusCode=500,
                message=f"No access token available for YouTube post {post['_id']}",
                responseBody="",
            )
        data = self.__get(post,token)
        stats = self.__parseResponse(data)
        print(f"✅ Fetched stats for YouTube post {post['_id']} from provider {self.provider} native api" )
        push_post_snapshots(stats, post['_id'])

        
        return stats


    def __get_youtube_video_id(self,url: str) -> str | None:
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

    def __parseResponse(self,response: Dict) -> List[Dict]:
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