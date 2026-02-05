import requests
import json
from post_success import push_post
import re




def get_TikTok(post):
    if post["status"] == 'Live':
        root = "https://www.ensembledata.com/apis"
        endpoint = "/tt/post/info"
        params = {
            "url": post['link'],
            "token": os.getenv("ENSEMBLE_TOKEN")
        }

        res = requests.get(root + endpoint, params=params)

        TikTokJson = json.loads(res.text)

        try:
            # Extract statistics
            plays = TikTokJson['data'][0]['statistics']["play_count"]
            likes = TikTokJson['data'][0]['statistics']["digg_count"]
            shares = TikTokJson['data'][0]['statistics']["share_count"]
            comments = TikTokJson['data'][0]['statistics']["comment_count"]
            saves = TikTokJson['data'][0]['statistics']["collect_count"]

            # Push post data
            push_post(
                plays=plays,
                likes=likes,
                shares=shares,
                comments=comments,
                saves=saves,
                post_id=post['_id']
            )

        except FileNotFoundError as e:
            print(f"File not found for post ID {post['_id']} with link {post['link']}: {e}")
        except json.decoder.JSONDecodeError as e:
            print(f"JSON Decoder Error for post ID {post['_id']} with link {post['link']}: {e}")
        except IndexError as e:
            print(f"Post removed or flagged (ID: {post['_id']}, Link: {post['link']}): {e}")
        except requests.exceptions.RequestException as e:
            print(f"HTTP Request Error for post ID {post['_id']} with link {post['link']}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred for post ID {post['_id']} with link {post['link']}: {e}")
        else:
            print(
                f'Post on {post["platform"]} has {plays} plays, {likes} likes, {shares} shares, {comments} comments, and {saves} saves\n'
            )

