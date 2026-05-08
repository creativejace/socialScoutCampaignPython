from bs4 import BeautifulSoup
import requests
import json
import re
import logging
from post_success import push_post, push_India_post
from shorts import get_shorts

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def find_yt_initial_data(soup):
    script = next(
        (s for s in soup.find_all('script') if s.string and 'ytInitialData' in s.string),
        None
    )
    if not script:
        raise json.decoder.JSONDecodeError("ytInitialData script not found", "", 0)

    script_content = script.string.strip()
    json_str_start = script_content.find("{")
    json_str_end = script_content.rfind("}")
    return json.loads(script_content[json_str_start:json_str_end + 1])


def extract_stats(data):
    contents = data['contents']['twoColumnWatchNextResults']['results']['results']['contents']
    primary = contents[0]['videoPrimaryInfoRenderer']

    views = primary['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
    views_int = int(re.sub(r'\D', '', views))

    almost_likes = str(
        primary['videoActions']['menuRenderer']['topLevelButtons'][0]
        ['segmentedLikeDislikeButtonViewModel']['likeButtonViewModel']['likeButtonViewModel']
        ['toggleButtonViewModel']['toggleButtonViewModel']['defaultButtonViewModel']
        ['buttonViewModel']['accessibilityText']
    )
    almost_likes_2 = almost_likes.split('this video along with ')
    almost_likes_3 = almost_likes_2[1].split(' other')
    likes = int(almost_likes_3[0].replace(',', ''))

    return views_int, likes


def get_youtube(post):
    if post['status'] != "Live":
        return

    link = post['link']
    creator_name = post.get('creator', {}).get('name', 'Unknown Creator')

    if '/shorts/' in link:
        logger.info(f'🩳 Short detected for {creator_name} — routing to get_shorts (post {post["_id"]})')
        get_shorts(post)
        return

    try:
        call = requests.get(url=link)
        soup = BeautifulSoup(call.text, 'html.parser')
        data = find_yt_initial_data(soup)
        views_int, likes = extract_stats(data)

        logger.info(f'📊 {creator_name} → Views: {views_int}, Likes: {likes}, Shares: 0, Comments: 0, Saves: 0 (post {post["_id"]})')

        push_post(
            plays=views_int,
            likes=likes,
            shares=0,
            comments=0,
            saves=0,
            post_id=post['_id']
        )

    except FileNotFoundError:
        logger.error('File not found')
    except json.decoder.JSONDecodeError as e:
        logger.error(f'JSON Not Found: {e}')
    except (KeyError, IndexError) as e:
        logger.error(f'Unexpected YouTube data structure: {e}')


def get_India_youtube(post):
    if post['status'] != "Live":
        return

    link = post['link']
    creator_name = post.get('creator', {}).get('name', 'Unknown Creator')

    if '/shorts/' in link:
        logger.info(f'🩳 Short detected for {creator_name} — routing to get_shorts (post {post["_id"]})')
        get_shorts(post)
        return

    try:
        call = requests.get(url=link)
        soup = BeautifulSoup(call.text, 'html.parser')
        data = find_yt_initial_data(soup)
        views_int, likes = extract_stats(data)

        logger.info(f'📊 {creator_name} → Views: {views_int}, Likes: {likes}, Shares: 0, Comments: 0, Saves: 0 (post {post["_id"]})')

        push_India_post(
            plays=views_int,
            likes=likes,
            shares=0,
            comments=0,
            saves=0,
            post_id=post['_id']
        )

    except FileNotFoundError:
        logger.error('File not found')
    except json.decoder.JSONDecodeError as e:
        logger.error(f'JSON Not Found: {e}')
    except (KeyError, IndexError) as e:
        logger.error(f'Unexpected YouTube data structure: {e}')