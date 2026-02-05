from bs4 import BeautifulSoup
import requests
import json
from post_success import push_post
import re
from shorts import get_shorts



def get_youtube(post):
    if post['status'] == "Live":
        link = post['link']
        if '/shorts/' in link:
            get_shorts(post)
            return  # Exit the function after handling shorts

        short_creator = post['creator']
        try:
            call = requests.get(url=link)
            soup = BeautifulSoup(call.text, 'html.parser')
            script_all = soup.find_all('script')
            script = script_all[45]
            script_content = script.string.strip() if script.string else ""
            json_str_start = script_content.find("{")
            json_str_end = script_content.rfind("}")
            json_string = script_content[json_str_start:json_str_end + 1]

            data = json.loads(json_string)
            views = data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
                'videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
            views_string = re.sub(r'\D', '', views)  # Remove all non-numeric characters
            views_int = int(views_string)
            almost_likes = str(data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
                                   'videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][0][
                                   'segmentedLikeDislikeButtonViewModel']['likeButtonViewModel']['likeButtonViewModel'][
                                   'toggleButtonViewModel']['toggleButtonViewModel']['defaultButtonViewModel'][
                                   'buttonViewModel']['accessibilityText'])
            almost_likes_2 = almost_likes.split('this video along with ')
            almost_likes_3 = almost_likes_2[1].split(' other')
            likes = int(almost_likes_3[0].replace(',', ''))
            comments = 0
            print(f'{post["creator"]["name"]} post has {views_int} plays')
            shares = 0
            saves = 0

            push_post(
                plays=views_int,
                likes=likes,
                shares=shares,
                comments=comments,
                saves=saves,
                post_id=post['_id']
            )


        except FileNotFoundError:
            print('File not found')
        except json.decoder.JSONDecodeError:
            print('JSON Not Found')

        else:
            print('\n')
            total_plays = 0
            total_comments = 0
            total_likes = 0

