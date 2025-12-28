from flask import Flask, request
import requests
import json
import os
import discord
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

CLIENT_ID = "1454583842110177371"
REDIRECT_URI = "https://verify-bot.onrender.com/callback"

GUILD_ID = 1454510378305327291
ROLE_IDS = [
    1454607108300603525,
    1454605263234535567
]
LOG_CHANNEL = 1454840923300298906

app = Flask(__name__)

def save_user(user_id):
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)

    with open("users.json", "r") as f:
        users = json.load(f)

    users[user_id] = True

    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

@app.route("/callback")
def callback():
    code = request.args.get("code")

    token_res = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "scope": "identify guilds.join"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).json()

    access_token = token_res["access_token"]

    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    user_id = user["id"]

    requests.put(
        f"https://discord.com/api/guilds/{GUILD_ID}/members/{user_id}",
        headers={
            "Authorization": f"Bot {BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={"access_token": access_token}
    )

    for role_id in ROLE_IDS:
        requests.put(
            f"https://discord.com/api/guilds/{GUILD_ID}/members/{user_id}/roles/{role_id}",
            headers={"Authorization": f"Bot {BOT_TOKEN}"}
        )

    save_user(user_id)

    return "✅ You are verified. You can close this tab."

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
