from flask import Flask, request
import requests, json, os

app = Flask(__name__)

# ===== ENV VARS =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# ===== IDS =====
CLIENT_ID = "1454583842110177371"
GUILD_ID = 1454510378305327291
LOG_CHANNEL_ID = 1454840923300298906

# ===== RAILWAY CALLBACK URL =====
# CHANGE AFTER DEPLOY
REDIRECT_URI = "https://your-project.up.railway.app/callback"

ROLES = [
    1454607108300603525,
    1454605263234535567
]

@app.route("/callback")
def callback():
    code = request.args.get("code")

    token = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).json()

    access_token = token.get("access_token")
    if not access_token:
        return "❌ Authorization failed."

    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    user_id = user["id"]

    # Save user for revive
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = {}

    users[user_id] = {"access_token": access_token}

    with open("users.json", "w") as f:
        json.dump(users, f)

    # Add to server
    requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}",
        headers={
            "Authorization": f"Bot {BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={"access_token": access_token}
    )

    # Give roles
    for role in ROLES:
        requests.put(
            f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}/roles/{role}",
            headers={"Authorization": f"Bot {BOT_TOKEN}"}
        )

    # Delete verify message
    try:
        with open("pending.json", "r") as f:
            pending = json.load(f)

        data = pending.get(user_id)
        if data:
            requests.delete(
                f"https://discord.com/api/v10/channels/{data['channel_id']}/messages/{data['message_id']}",
                headers={"Authorization": f"Bot {BOT_TOKEN}"}
            )
            pending.pop(user_id)
            with open("pending.json", "w") as f:
                json.dump(pending, f)
    except:
        pass

    # Log verification
    requests.post(
        f"https://discord.com/api/v10/channels/{LOG_CHANNEL_ID}/messages",
        headers={
            "Authorization": f"Bot {BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={"content": f"✅ <@{user_id}> verified and roles assigned."}
    )

    return "✅ Verified! You can close this tab."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))