import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# ===== ENV VARS =====
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===== IDS =====
GUILD_ID = 1454510378305327291
VERIFY_CHANNEL_ID = 1454834468115452026
LOG_CHANNEL_ID = 1454840923300298906
OWNER_ID = 413597092867735552

# ===== OAUTH LINK (Railway URL ENCODED) =====
# CHANGE "your-project.up.railway.app" AFTER DEPLOY
OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
    "?client_id=1454583842110177371"
    "&response_type=code"
    "&redirect_uri=https%3A%2F%2Fyour-project.up.railway.app%2Fcallback"
    "&scope=identify+guilds.join"
)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"✅ Logged in as {bot.user}")
    print("✅ Slash commands synced")

@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(VERIFY_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="🔐 Verification Required",
        description="Click the button below to verify.",
        color=0x5865F2
    )

    view = discord.ui.View(timeout=None)
    view.add_item(discord.ui.Button(label="Verify", url=OAUTH_URL))

    msg = await channel.send(member.mention, embed=embed, view=view)

    # Save message for deletion later
    try:
        with open("pending.json", "r") as f:
            pending = json.load(f)
    except:
        pending = {}

    pending[str(member.id)] = {
        "channel_id": msg.channel.id,
        "message_id": msg.id
    }

    with open("pending.json", "w") as f:
        json.dump(pending, f)

# =====================
# /REVIVE COMMAND
# =====================
@bot.tree.command(
    name="revive",
    description="Re-add all verified users",
    guild=discord.Object(id=GUILD_ID)
)
async def revive(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=True)

    if interaction.user.id != OWNER_ID:
        await interaction.followup.send("❌ You are not allowed.", ephemeral=True)
        return

    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        await interaction.followup.send("❌ No users to revive.", ephemeral=True)
        return

    import requests

    success = 0
    failed = 0

    for user_id, data in users.items():
        r = requests.put(
            f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}",
            headers={
                "Authorization": f"Bot {BOT_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"access_token": data["access_token"]}
        )

        if r.status_code in (201, 204):
            success += 1
        else:
            failed += 1

    await interaction.followup.send(
        f"🧟 **Revive complete**\n"
        f"✅ Joined: **{success}**\n"
        f"❌ Failed: **{failed}**",
        ephemeral=True
    )

    log = interaction.guild.get_channel(LOG_CHANNEL_ID)
    if log:
        await log.send(
            f"🧟 **Revive used by {interaction.user}**\n"
            f"✅ Joined: {success}\n"
            f"❌ Failed: {failed}"
        )

bot.run(BOT_TOKEN)