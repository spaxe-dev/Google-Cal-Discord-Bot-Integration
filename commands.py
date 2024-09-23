from discord.ext import commands
from google_calendar import fetch_events_of_this_week, fetch_events_from_today, fetch_today
from utils import load_sent_event_ids, save_sent_event_ids
from config import set_channel_id, get_channel_id

# Load sent event IDs
sent_event_ids = load_sent_event_ids()

def setup(bot):
    @bot.command()
    async def setup(ctx):
        set_channel_id(ctx.channel.id)  # Use the setter function
        await ctx.send(f"Channel ID set to {get_channel_id()}")  # Use the getter for confirmation
        print(f"Channel ID set to: {get_channel_id()}")  # Debugging

    @bot.command()
    async def ping(ctx):
        await ctx.send("Pong!")

    # Added this to fetch from today to next Monday
    @bot.command()
    async def fetchTodayToMonday(ctx):
        if fetch_events_from_today.is_running():
            await ctx.send("Fetching events is already running.")
        else:
            fetch_events_from_today.start()  # Start the fetching task
            await ctx.send("Started fetching events.")
            
    # Added this to fetch from today's events
    @bot.command()
    async def fetchToday(ctx):
        if fetch_today.is_running():
            await ctx.send("Fetching events is already running.")
        else:
            fetch_today.start()  # Start the fetching task
            await ctx.send("Started fetching events.")
    
    @bot.command()
    async def clearsent(ctx):
        global sent_event_ids  
        sent_event_ids = set()  # Clear the set in memory
        save_sent_event_ids(sent_event_ids)  # Save to JSON
        await ctx.send("Cleared all sent event IDs.")

    @bot.command()
    async def stopfetch(ctx):
        fetch_events_of_this_week.stop()  # Stop the fetching task
        await ctx.send("Stopped fetching events.")

    @bot.command()
    async def startfetch(ctx):
        if fetch_events_of_this_week.is_running():
            await ctx.send("Fetching events is already running.")
        else:
            fetch_events_of_this_week.start()  # Start the fetching task
            await ctx.send("Started fetching events.")
