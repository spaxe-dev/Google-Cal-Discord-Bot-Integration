import os, json, pytz, discord
from datetime import datetime, timedelta
from discord.ext import tasks
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from utils import load_sent_event_ids, save_sent_event_ids
from config import calendar_ids, channel_id, get_channel_id
# Global variable to store the bot instance
bot = None

def initialize_calendar(bot_instance):
    global bot
    bot = bot_instance


# Setting timezone
Timezone_IST = pytz.timezone('Asia/Kolkata')

# Setting up API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Load sent event IDs
sent_event_ids = load_sent_event_ids()

# Defining the function that will fetch events from THIS MONDAY to next monday
@tasks.loop(seconds=15)  # Check for events every 15 seconds
async def fetch_events_of_this_week():
    service = get_service()
    now = datetime.now(Timezone_IST).replace(microsecond=0).isoformat()
    # Finding this week monday
    current_monday = (now - timedelta(days=now.weekday())).isoformat()
    # Find next week Monday
    next_monday = (current_monday + timedelta(days=7)).isoformat()

    # Fetch events starting from this Monday to next Monday
    events_result = service.events().list(
        calendarId='primary',
        timeMin=current_monday, # From this week monday
        timeMax=next_monday,  # To next week Monday
        singleEvents=True,
        orderBy='startTime'  
    ).execute()

    events = events_result.get('items', [])

    # If there's no events send the response and return
    if not events:
            print('No events this week.')
            await channel.send('No events this week.') 
            return 
    all_events = []    
    for event in events:
        event_id = event['id']
        if event_id not in sent_event_ids:
            start = event['start'].get('dateTime', event['start'].get('date'))
            all_events.append((start, event['summary'], event_id))
        
    # Sort events by start time
    all_events.sort(key=lambda x: x[0])

    # Single Embed
    embed = discord.Embed(
        title="Upcoming Events This Week",
        description="Here are the upcoming events from your Google Calendar:",
        color=discord.Color.blurple()
    )

    for start, summary, event_id in all_events:
        start_datetime = datetime.fromisoformat(start)
        event_date = start_datetime.strftime('%A, %Y-%m-%d')  
        event_time = start_datetime.strftime('%I:%M %p') 
        
        embed.add_field(
            name=f"{summary}",
            value=f"**Date**: {event_date}\n**Time**: {event_time}\n**----------------------**",
            inline=False
        )
        sent_event_ids.add(event_id)
    
    save_sent_event_ids(sent_event_ids) #saving all the ids at once
    await channel.send(embed=embed)
    

# Defining the function that will fetch events from TODAY to next monday
# THIS FUNCTION DOES'NT REPEAT AFTER 15 SECONDS, THAT'S WHY IT DOES'NT KEEP TRACK OF SENT IDS, PUT A LIMITER ON THIS FUNCTION IF REQUIRED
async def fetch_events_from_today():
    channel_id = get_channel_id()
    if channel_id is None:
        print("Channel ID is not set. Use the `setup` command to set it.")
        return
    
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("Channel not found. Please check the channel ID.")
        return
    
    service = get_service()
    now = datetime.now(Timezone_IST).replace(microsecond=0).isoformat()
    one_week_later = (datetime.now(Timezone_IST) + timedelta(weeks=1)).replace(microsecond=0).isoformat()
    
    print(f"Fetching events between {now} and {one_week_later}")
    for calendar_id in calendar_ids:
        print(f"Fetching events from calendar: {calendar_id}")
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            timeMax=one_week_later,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

    events = events_result.get('items', [])
    
        # Single Embed
    embed = discord.Embed(
    title="Upcoming Events This Week",
    description="Here are the upcoming events from your Google Calendar:",
    color=discord.Color.blurple()
)

    for event in events:
        start_datetime = datetime.fromisoformat(event['start']['datetime'])
        event_date = start_datetime.strftime('%A, %Y-%m-%d')  
        event_time = start_datetime.strftime('%I:%M %p') 
        
        embed.add_field(
            name=f"{event['summary']}",
            value=f"**Date**: {event_date}\n**Time**: {event_time}\n**----------------------**",
            inline=False
        )

    await channel.send(embed=embed)
    
async def fetch_today():
    channel_id = get_channel_id()
    if channel_id is None:
        print("Channel ID is not set. Use the `setup` command to set it.")
        return
    
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("Channel not found. Please check the channel ID.")
        return
    
    service = get_service()
    now = datetime.now(Timezone_IST).replace(microsecond=0).isoformat()
    start = now.replace(hour=0, minute=0, second=0).isoformat()
    end = (now.replace(hour=23, minute=59, second=59)).isoformat()
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    # If there's no events send the response and return
    if not events:
            print('No events this week.')
            await channel.send('No events this week.') 
            return 
    
    # USE EMBED TO CUSTOMIZE THE EVENTS AND THEN SEND IT
    sendingText = ''
    for event in events:
        start_datetime = datetime.fromisoformat(event['start']['datetime'])
        event_date = start_datetime.strftime('%A, %Y-%m-%d')  
        event_time = start_datetime.strftime('%I:%M %p)
        sendingText += f'{event['id']} | summary: {event['summary']} | date: {event_date}| time: {event_time}'
    await channel.send(sendingText);
    # DONT SAVE THE EVENT IDS AS THIS COMMAND WILL NOT BE EXECUTED AUTOMATICALLY RATHER USED BY PEOPLE
    
def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)
