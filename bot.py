import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import logging

GUILD_ID = 1454510378305327291
VERIFY_CHANNEL_ID = 1454834468115452026
LOG_CHANNEL_ID = 1454840923300298906

ROLE_IDS = [
    1454607108300603525,
    1454605263234535567
]

OAUTH_URL = "https://discord.com/oauth2/authorize?client_id=1454583842110177371&response_type=code&redirect_uri=https://verify-bot-wdim.onrender.com/callback&scope=identify+guilds.join"

PENDING_FILE = "pending.json"
USERS_FILE = "users.json"


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

logging.basicConfig(level=logging.INFO)


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.link, url=OAUTH_URL)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass


@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Logged in as {bot.user}")


@tree.command(name="revive", description="Resend verification to unverified users", guild=discord.Object(id=GUILD_ID))
async def revive(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    pending = load_json(PENDING_FILE)
    users = load_json(USERS_FILE)

    guild = bot.get_guild(GUILD_ID)
    verify_channel = guild.get_channel(VERIFY_CHANNEL_ID)

    revived = 0

    for user_id in list(pending.keys()):
        member = guild.get_member(int(user_id))
        if not member:
            continue

        if user_id in users:
            continue

        embed = discord.Embed(
            title="🔒 Verification Required",
            description="Click the button below to verify.",
            color=discord.Color.blurple()
        )

        await verify_channel.send(
            content=f"Welcome {member.mention}! Please verify to get access.",
            embed=embed,
            view=VerifyView()
        )

        revived += 1

    await interaction.followup.send(
        f"✅ Revive complete. `{revived}` users were re-sent verification.",
        ephemeral=True
    )


async def handle_verified_user(user_id: int):
    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(user_id)
    if not member:
        return

    for role_id in ROLE_IDS:
        role = guild.get_role(role_id)
        if role:
            await member.add_roles(role)

    users = load_json(USERS_FILE)
    users[str(user_id)] = True
    save_json(USERS_FILE, users)

    pending = load_json(PENDING_FILE)
    pending.pop(str(user_id), None)
    save_json(PENDING_FILE, pending)

    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"✅ **{member}** has verified successfully.")


def run_bot():
    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
