from bs4 import BeautifulSoup
import requests
import json
import re
import logging
from post_success import push_post

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def parse_abbreviated_number(text):
    """Handle formats like 1,234 or 1.2K or 4.5M"""
    text = text.strip().replace(',', '')
    if text.endswith('K'):
        return int(float(text[:-1]) * 1_000)
    elif text.endswith('M'):
        return int(float(text[:-1]) * 1_000_000)
    elif text.endswith('B'):
        return int(float(text[:-1]) * 1_000_000_000)
    else:
        return int(re.sub(r'\D', '', text))


def find_yt_initial_data(soup):
    script = next(
        (s for s in soup.find_all('script') if s.string and 'ytInitialData' in s.string),
        None
    )
    if not script:
        raise ValueError("ytInitialData script not found")

    script_content = script.string.strip()
    json_str_start = script_content.find("{")
    json_str_end = script_content.rfind("}")
    return json.loads(script_content[json_str_start:json_str_end + 1])


def extract_shorts_stats(data, raw_html):
    view_count = 0
    like_count = 0
    comment_count = 0

    button_view_models = (
        data.get('overlay', {})
            .get('reelPlayerOverlayRenderer', {})
            .get('buttonBar', {})
            .get('reelActionBarViewModel', {})
            .get('buttonViewModels', [])
    )

    # --- Likes ---
    try:
        like_title = (
            button_view_models[0]['likeButtonViewModel']
            ['toggleButtonViewModel']['toggleButtonViewModel']
            ['defaultButtonViewModel']['buttonViewModel']['title']
        )
        like_count = parse_abbreviated_number(like_title)
    except (KeyError, IndexError, ValueError) as e:
        logger.warning(f'⚠️ Could not extract likes: {e}')

    # --- Comments ---
    try:
        comment_title = button_view_models[2]['buttonViewModel']['title']
        comment_count = parse_abbreviated_number(comment_title)
    except (KeyError, IndexError, ValueError) as e:
        logger.warning(f'⚠️ Could not extract comments: {e}')

    # --- Views: from description panel ---
    try:
        views_text = (
            data['engagementPanels'][1]['engagementPanelSectionListRenderer']
            ['content']['structuredDescriptionContentRenderer']['items'][0]
            ['videoDescriptionHeaderRenderer']['views']['simpleText']
        )
        view_count = parse_abbreviated_number(views_text)
    except (KeyError, IndexError, ValueError) as e:
        logger.warning(f'⚠️ Could not extract views from description panel: {e}')

    return view_count, like_count, comment_count

def get_shorts(post):
    if post['status'] != "Live":
        return

    logger.info("YouTube Short identified")
    creator_name = post.get('creator', {}).get('name', 'Unknown Creator')

    try:
        call = requests.get(url=post['link'])
        soup = BeautifulSoup(call.text, 'html.parser')
        data = find_yt_initial_data(soup)

        # 🔍 DEBUG: Log full ytInitialData JSON
        logger.info("ytInitialData dump:\n%s", json.dumps(data, indent=2, ensure_ascii=False))

        view_count, like_count, comment_count = extract_shorts_stats(data, call.text)

        logger.info(f'📊 {creator_name} → Views: {view_count}, Likes: {like_count}, Comments: {comment_count}, Shares: 0, Saves: 0 (post {post["_id"]})')

        push_post(
            plays=view_count,
            likes=like_count,
            shares=0,
            comments=comment_count,
            saves=0,
            post_id=post['_id']
        )

    except requests.RequestException as e:
        logger.error(f'Network error: {e}')
    except ValueError as e:
        logger.error(f'Data extraction error: {e}')
    except (KeyError, IndexError) as e:
        logger.error(f'Unexpected data structure: {e}')
    except json.decoder.JSONDecodeError as e:
        logger.error(f'JSON parse error: {e}')