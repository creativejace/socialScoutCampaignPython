# from bs4 import BeautifulSoup
# import requests
# import json
# import re
# from post_success import push_post


# def get_shorts(post):
#     if post['status'] == "Live":
#         short = post['link']
#         print("YouTube Short identified")

#         try:
#             call = requests.get(url=short)
#             soup = BeautifulSoup(call.text, 'html.parser')
#             scripts = soup.find_all('script')  # Get all script tags

#             like_count = 0  # Default to 0
#             comment_count = 0  # Default to 0
#             view_count = 0  # Default to 0
#             found_script_index = None  # Track which script contains the data

#             # Iterate through script tags to find the one containing views, likes, and comments
#             for index, script in enumerate(scripts):
#                 if script.string and ('"views":' in script.string or '"accessibilityData":' in script.string):
#                     found_script_index = index
#                     print(f"\n✅ Found relevant script at index #{index}")
#                     print("------ Script Content Start ------")
#                     print(script.string[:1000])  # Print first 1000 chars for debugging
#                     print("------ Script Content End ------\n")

#                     try:
#                         # Extract JSON-like content
#                         json_text = re.search(r'\{.*\}', script.string, re.DOTALL)
#                         if json_text:
#                             data = json.loads(json_text.group(0))

#                             # ✅ Extract View Count from "views":{"simpleText":"X views"}
#                             view_match = re.search(r'"views":\{"simpleText":"([\d,]+) views"\}', script.string)
#                             if view_match:
#                                 view_count = int(view_match.group(1).replace(",", ""))

#                             # ✅ Extract Likes
#                             like_match = re.search(r'"accessibilityData":\{"label":"([\d,]+) likes"', script.string)
#                             if like_match:
#                                 like_count = int(like_match.group(1).replace(",", ""))

#                             # ✅ Extract Comments
#                             comment_match = re.search(r'"accessibility":\{"label":"View (\d+(?:,\d+)*) comments"', script.string)
#                             if comment_match:
#                                 comment_count = int(comment_match.group(1).replace(",", ""))

#                         break  # Stop looping once found

#                     except json.JSONDecodeError:
#                         print(f"⚠️ JSON Decode Error in script #{index}")
#                         continue  # Skip if there's an issue parsing JSON

#             if found_script_index is None:
#                 print("❌ No script containing relevant data was found.")

#             # Update global totals
#             global total_plays, total_likes, total_comments
#             total_plays = view_count
#             total_likes = like_count
#             total_comments = comment_count
#             shares = 0
#             saves = 0

#             print(f'📊 Extracted Data → Views: {total_plays}, Likes: {total_likes}, Comments: {total_comments} in post {post["_id"]}')

#             # Push data to post
#             push_post(
#                 plays=total_plays,
#                 likes=total_likes,
#                 shares=shares,
#                 comments=total_comments,
#                 saves=saves,
#                 post_id=post['_id']
#             )

#         except requests.RequestException:
#             print('❌ Network error')
#         except FileNotFoundError:
#             print('❌ File not found')
#         except json.decoder.JSONDecodeError:
#             print('❌ JSON Not Found')

#         else:
#             print('\n')
#             total_plays = 0
#             total_comments = 0
#             total_likes = 0


import requests
import os
from datetime import datetime
from post_success import push_post

# Extract video ID from Shorts URL
def extract_video_id(url):
    if "shorts/" in url:
        return url.split("shorts/")[1].split("?")[0]
    return None


def get_shorts(post):
    if post['status'] != "Live":
        return

    print("🎬 Processing YouTube Shorts")

    try:
        video_id = extract_video_id(post['link'])

        if not video_id:
            print("❌ Invalid Shorts URL")
            return

        API_KEY = os.getenv("YOUTUBE_API_KEY")

        url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={API_KEY}"

        response = requests.get(url)
        data = response.json()

        if "items" not in data or len(data["items"]) == 0:
            print("❌ No data found from YouTube API")
            return

        stats = data["items"][0]["statistics"]

        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        shares = 0
        saves = 0

        print(f"📊 Stats → Views: {views}, Likes: {likes}, Comments: {comments}")

        # Push to MongoDB
        push_post(
            plays=views,
            likes=likes,
            shares=shares,
            comments=comments,
            saves=saves,
            post_id=post['_id']
        )

    except Exception as e:
        print(f"❌ Error: {e}")