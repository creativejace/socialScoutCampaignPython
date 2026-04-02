from shorts import get_shorts
from instagram import get_Instagram
from tiktok import get_TikTok
from youtube import get_youtube
from services.token_service import get_access_token
from core.registry import get_platform_client
from campaign_fetcher import get_campaign_with_latest_snapshot



def get_posts(post):
    print(post["platform"])
    try:
        if post['platform'] == 'tiktok':
            get_TikTok(post)
            print("tiktok")
        elif post['platform'] == 'instagram':
            get_Instagram(post)
            print("instagram")

        elif post['platform'] == 'youtube':
            get_youtube(post)


    except Exception as e:
        print(f"Post parse error: ", e)


def get_posts2(post):
    """ Process the post based on its platform """
    print(f"Processing post from platform: {post['platform']}")

    try:

        token = get_access_token(post['platform'], post['_id'])
        client = get_platform_client(post['platform'], token)

        client.get_stats(post)
        print(f"✅ {post['platform']} post processed")
    

    except Exception as e:
        print(f"❌ Error processing post: {e}")