# Store your bot token here
BOT_TOKEN = 'Your_Bot_Token'

channel_id = None  # Global variable to store the channel ID

def set_channel_id(channel):
    global channel_id
    channel_id = channel

def get_channel_id():
    return channel_id

# Calendar IDs
calendar_ids = [
    'Your calendar ID',
    'Your calendar ID',
    'Your calendar ID',
    'Your calendar ID',
]
