import requests
import json
from post_success import push_post
from urllib.parse import urlparse
from post_success import push_India_post
def get_Instagram(post):
    print( post["status"])




    url = post['link']
    parsed_url = urlparse(url)

    # The path attribute of the parsed URL will give '/reel/CyEhNnTyObD/'
    path_parts = parsed_url.path.split('/')
    reel_id = path_parts[2]  # This will give 'CyEhNnTyObD'


    root = "https://www.ensembledata.com/apis"
    endpoint = "/instagram/post/details"
    params = {
        "code": reel_id,
        "n_comments_to_fetch": "0",
        "token": "vpvBnFjSneVMJtDK"
    }

    res = requests.get(root + endpoint, params=params)

    InstagramJson = json.loads(res.text)
    print("This is the Insta JSON: ", InstagramJson)


    try:
        plays = InstagramJson['data']["video_play_count"]
        likes = InstagramJson['data']["edge_media_preview_like"]["count"]
        comments = InstagramJson['data']['edge_media_to_comment']["count"]
        shares = 0
        saves = 0

        push_post(
            plays=plays,
            likes=likes,
            shares=shares,
            comments=comments,
            saves=saves,
            post_id=post['_id']
        )
    except FileNotFoundError:
        print("File not found")
    except json.decoder.JSONDecodeError:
        print("JSON Decoder Error")
    except IndexError:
        print("post removed or flagged")


    else:
        print("Instagram added")


def get_India_Instagram(post):
    if post["status"] == 'Live':



        url = post['link']
        parsed_url = urlparse(url)

        # The path attribute of the parsed URL will give '/reel/CyEhNnTyObD/'
        path_parts = parsed_url.path.split('/')
        reel_id = path_parts[2]  # This will give 'CyEhNnTyObD'


        root = "https://www.ensembledata.com/apis"
        endpoint = "/instagram/post/details"
        params = {
            "code": reel_id,
            "n_comments_to_fetch": "0",
            "token": "vpvBnFjSneVMJtDK"
        }

        res = requests.get(root + endpoint, params=params)

        InstagramJson = json.loads(res.text)

        try:
            plays = InstagramJson['data']["video_play_count"]
            likes = InstagramJson['data']["edge_media_preview_like"]["count"]
            comments = InstagramJson['data']['edge_media_to_comment']["count"]
            shares = 0
            saves = 0

            push_India_post(
                plays=plays,
                likes=likes,
                shares=shares,
                comments=comments,
                saves=saves,
                post_id=post['_id']
            )

        except FileNotFoundError:
            print("File not found")
        except json.decoder.JSONDecodeError:
            print("JSON Decoder Error")
        except IndexError:
            print("post removed or flagged")


        else:
            print("Instagram added")
