import discord
from discord.ext import commands
from commands import setup
from google_calendar import fetch_events
from config import BOT_TOKEN
from google_calendar import initialize_calendar  # Import the initialization function


# Setting up intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix="`", intents=intents)
initialize_calendar(bot)                           

@bot.event
async def on_ready():
    print(f'Bot is ready and logged in as {bot.user}')
    fetch_events.start()  # Start fetching events when the bot is ready

# Register commands
setup(bot)

# Start the bot
bot.run(BOT_TOKEN)
