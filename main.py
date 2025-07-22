
from flask import Flask, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "X-IG-App-ID": "936619743392459",
    "X-Requested-With": "XMLHttpRequest"
}

def fetch_profile(username):
    params = {
        "query_hash": "9b498c08113f1e09617a1703c22b2f32",
        "variables": f'{{"username":"{username}","first":12}}'
    }
    return requests.get(
        "https://www.instagram.com/graphql/query/",
        headers=HEADERS,
        params=params
    )

@app.route('/<username>', methods=['GET'])
def profile(username):
    response = fetch_profile(username)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data", "status_code": response.status_code})

    try:
        user_data = response.json().get("data", {}).get("user", {})
        if not user_data:
            return jsonify({"error": "User not found"})

        timeline = user_data.get("edge_owner_to_timeline_media", {})
        posts = [
            {
                "Post ID": post["node"]["id"],
                "Caption": post["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
                if post["node"]["edge_media_to_caption"]["edges"] else "No Caption",
                "Likes": post["node"]["edge_liked_by"]["count"],
                "Comments": post["node"]["edge_media_to_comment"]["count"],
                "Post URL": f"https://www.instagram.com/p/{post['node']['shortcode']}/",
                "Thumbnail": post["node"]["display_url"],
                "Type": "Video" if post["node"]["is_video"] else "Image"
            }
            for post in timeline.get("edges", [])
        ]

        return jsonify({
            "Profile Info": {
                "Username": user_data.get("username"),
                "Full Name": user_data.get("full_name"),
                "Bio": user_data.get("biography"),
                "Followers": user_data.get("edge_followed_by", {}).get("count"),
                "Following": user_data.get("edge_follow", {}).get("count"),
                "Total Posts": timeline.get("count"),
                "Profile Picture": user_data.get("profile_pic_url_hd"),
                "Private Account": user_data.get("is_private"),
            },
            "Recent Posts": posts
        })
    except Exception as e:
        return jsonify({"error": "Failed to parse response", "details": str(e)})

if __name__ == '__main__':
    app.run()
