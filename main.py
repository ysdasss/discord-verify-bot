import os
import threading
from dotenv import load_dotenv

from bot import run_bot
from web import run_web

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

def main():
    # Start Flask OAuth server
    threading.Thread(target=run_web, daemon=True).start()

    # Start Discord bot
    run_bot(BOT_TOKEN)

if __name__ == "__main__":
    main()
