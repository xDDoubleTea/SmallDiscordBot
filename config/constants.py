from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
MONITOR_CHANNEL_ID = os.getenv("MONITOR_CHANNEL_ID")
# You can use a list of ids if you want, though that will be too complex for this bot.
PREFIX = os.getenv("PREFIX")
if not PREFIX:
    PREFIX = ""
application_id = 1
# Your app id here
