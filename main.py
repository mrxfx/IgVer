from flask import Flask, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36 Instagram 155.0.0.37.107 Android (28/9; 320dpi; 720x1468; samsung; SM-G960F; starlte; samsungexynos9810; en_US; 239490550)",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    # Add if you have it:
    # "Cookie": "sessionid=YOUR_SESSION_ID"
}

def fetch_profile(username):
    try:
        # Try public endpoint first
        response = requests.get(
            f"https://www.instagram.com/{username}/?__a=1&__d=dis",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 404:
            return {"error": "User not found"}, 404
            
        return response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500

@app.route('/<username>', methods=['GET'])
def profile(username):
    response = fetch_profile(username)
    
    if isinstance(response, tuple):  # Error case
        return jsonify(response[0]), response[1]
        
    if response.status_code != 200:
        return jsonify({
            "error": "Failed to fetch data",
            "status_code": response.status_code,
            "message": response.text
        }), response.status_code

    try:
        data = response.json()
        user_data = data.get("graphql", {}).get("user", {})
        
        if not user_data:
            return jsonify({"error": "User data not found in response"}), 404

        posts = []
        for post in user_data.get("edge_owner_to_timeline_media", {}).get("edges", []):
            post_node = post.get("node", {})
            posts.append({
                "id": post_node.get("id"),
                "caption": post_node.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text"),
                "likes": post_node.get("edge_liked_by", {}).get("count"),
                "comments": post_node.get("edge_media_to_comment", {}).get("count"),
                "url": f"https://www.instagram.com/p/{post_node.get('shortcode')}/",
                "thumbnail": post_node.get("display_url"),
                "is_video": post_node.get("is_video")
            })

        return jsonify({
            "username": user_data.get("username"),
            "full_name": user_data.get("full_name"),
            "bio": user_data.get("biography"),
            "followers": user_data.get("edge_followed_by", {}).get("count"),
            "following": user_data.get("edge_follow", {}).get("count"),
            "posts_count": user_data.get("edge_owner_to_timeline_media", {}).get("count"),
            "profile_pic": user_data.get("profile_pic_url_hd"),
            "is_private": user_data.get("is_private"),
            "posts": posts
        })
        
    except Exception as e:
        return jsonify({
            "error": "Failed to parse response",
            "details": str(e),
            "raw_response": response.text[:500] + "..." if response.text else None
        }), 500

if __name__ == '__main__':
    app.run(port=5000)
