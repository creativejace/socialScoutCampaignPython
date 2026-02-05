from bs4 import BeautifulSoup
import requests
import json
import re
from post_success import push_post


def get_shorts(post):
    if post['status'] == "Live":
        short = post['link']
        print("YouTube Short identified")

        try:
            call = requests.get(url=short)
            soup = BeautifulSoup(call.text, 'html.parser')
            scripts = soup.find_all('script')  # Get all script tags

            # Extract Views from meta tag
            views_meta = soup.find('meta', {'itemprop': 'interactionCount'})
            views = int(views_meta['content']) if views_meta else 0

            like_count = 0  # Default to 0
            comment_count = 0  # Default to 0
            found_script_index = None  # To track which script contains the data

            # Iterate through script tags to find the one containing "accessibilityData"
            for index, script in enumerate(scripts):
                if script.string and '"accessibilityData":' in script.string:
                    found_script_index = index
                    print(f"\n✅ Found 'accessibilityData' in script #{index}")
                    print("------ Script Content Start ------")
                    print(script.string[:1000])  # Print first 1000 chars for debugging
                    print("------ Script Content End ------\n")

                    try:
                        # Extract JSON-like content
                        match = re.search(r'"accessibilityData":\{.*?\}', script.string)
                        if match:
                            json_text = '{' + match.group(0) + '}'
                            data = json.loads(json_text)

                            # Extract Likes
                            label_text = data.get("accessibilityData", {}).get("label", "")
                            like_match = re.search(r'(\d+(?:,\d+)*)', label_text)
                            if like_match:
                                like_count = int(like_match.group(0).replace(",", ""))

                        # Extract Comments
                        comment_match = re.search(r'"accessibility":\{"label":"View (\d+(?:,\d+)*) comments"', script.string)
                        if comment_match:
                            comment_count = int(comment_match.group(1).replace(",", ""))

                        break  # Stop looping once found
                    except json.JSONDecodeError:
                        print(f"⚠️ JSON Decode Error in script #{index}")
                        continue  # Skip if there's an issue parsing JSON

            if found_script_index is None:
                print("❌ No script containing 'accessibilityData' was found.")

            likes = like_count
            comments = comment_count  # Extracted comment count

            # Update global totals
            global total_plays, total_likes, total_comments
            total_plays = views
            total_likes = likes
            total_comments = comments
            shares = 0
            saves = 0
            print(f'There were {total_plays} plays, {total_likes} likes, and {total_comments} comments in post {post["_id"]}')
            # Push data to post
            push_post(
                plays=total_plays,
                likes=total_likes,
                shares=shares,
                comments=total_comments,
                saves=saves,
                post_id=post['_id']
            )

            # Debugging Output
            print(f"\n✅ Extracted Data:\n - Views: {views}\n - Likes: {likes}\n - Comments: {comments}\n")

        except requests.RequestException:
            print('❌ Network error')
        except FileNotFoundError:
            print('❌ File not found')
        except json.decoder.JSONDecodeError:
            print('❌ JSON Not Found')

        else:
            print('\n')
            total_plays = 0
            total_comments = 0
            total_likes = 0