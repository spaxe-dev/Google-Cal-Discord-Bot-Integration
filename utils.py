import json, os

def load_sent_event_ids():
    if os.path.exists('sent_events.json'):
        with open('sent_events.json', 'r') as file:
            return set(json.load(file))
    return set()

def save_sent_event_ids(sent_event_ids):
    with open('sent_events.json', 'w') as file:
        json.dump(list(sent_event_ids), file)
