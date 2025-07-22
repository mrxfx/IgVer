from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36 Instagram 155.0.0.37.107 Android (28/9; 320dpi; 720x1468; samsung; SM-G960F; starlte; samsungexynos9810; en_US; 239490550)",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_profile(username):
    try:
        # Using the public JSON endpoint
        url = f"https://www.instagram.com/{username}/channel/?__a=1&__d=dis"
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response
    except Exception as e:
        return None

@app.route('/<username>')
def profile(username):
    response = fetch_profile(username)
    
    if not response or response.status_code != 200:
        return jsonify({
            "error": "Failed to fetch data",
            "status_code": response.status_code if response else 500,
            "message": response.text if response else "Request failed"
        }), response.status_code if response else 500

    try:
        data = response.json()
        user_data = data.get("graphql", {}).get("user", {})
        
        if not user_data:
            return jsonify({"error": "User data not found"}), 404

        return jsonify({
            "username": user_data.get("username"),
            "full_name": user_data.get("full_name"),
            "bio": user_data.get("biography"),
            "followers": user_data.get("edge_followed_by", {}).get("count"),
            "following": user_data.get("edge_follow", {}).get("count"),
            "profile_pic": user_data.get("profile_pic_url_hd"),
            "is_private": user_data.get("is_private")
        })
        
    except Exception as e:
        return jsonify({
            "error": "Failed to parse response",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run()
