from shorts import get_shorts
from instagram import get_Instagram
from tiktok import get_TikTok
from youtube import get_youtube



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

