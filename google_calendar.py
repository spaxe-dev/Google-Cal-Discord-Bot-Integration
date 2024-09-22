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


# Define fetch_events task
@tasks.loop(seconds=15)  # Check for events every 15 seconds
async def fetch_events():
    channel_id = get_channel_id()  # Get the channel ID from config.py
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
    all_events = []

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
        if not events:
            print('No upcoming events found.')
            await channel.send("No events this week.")
            continue
        
        for event in events:
            event_id = event['id']
            if event_id not in sent_event_ids:
                start = event['start'].get('dateTime', event['start'].get('date'))
                all_events.append((start, event['summary'], event_id))

    # Sort events by start time
    all_events.sort(key=lambda x: x[0])  # Sort by the first element (start time)

    # Send messages in sorted order
    for start, summary, event_id in all_events:
        message = f"Upcoming event: {summary} at {start}"
        await channel.send(message)
        sent_event_ids.add(event_id)
        save_sent_event_ids(sent_event_ids)

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
