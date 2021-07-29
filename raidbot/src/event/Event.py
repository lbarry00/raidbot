import datetime
import json
from json import JSONEncoder, JSONDecodeError
from raidbot.src.event.EventData import EventData


class Event:
    player_count: int
    activity: str
    type: str
    id: str
    start_time: datetime
    accepted_players: []
    tentative_players: []
    declined_players: []

    json_file_location = "../event/events.json"

    def __init__(self, activity_short_name, **kwargs):
        event_data = EventData("../bot/config/config.json")
        event_data.parse_and_setup()
        event_info = event_data.get_single_event(activity_short_name)
        # initialize event variables
        self.player_count = event_info["player_count"]
        self.activity = event_info["long_name"]
        self.type = event_info["type"]
        self.accepted_players = []
        self.declined_players = []
        self.tentative_players = []

    @staticmethod
    def backup_events(event):
        """Append event argument to json file events.json"""
        # vars is pythonic way of saying Event's dictionary, a dictionary representation of the class
        # default=str converts datetime to str cuz not serializable by python json library
        # TODO: fix json file appending
        try:
            with open(Event.json_file_location, 'a') as file:
                event_dict = json.load(file)
                event_dict.update(vars(event))
                #file.seek(0)
                file.write(json.dumps(event_dict, indent=4, default=str))
                file.close()
        except FileNotFoundError:
            with open(Event.json_file_location, 'w') as file:
                file.write(json.dumps(vars(event), indent=4, default=str))
                file.close()
        except ValueError:
            with open(Event.json_file_location, 'w') as file:
                file.write(json.dumps(vars(event), indent=4, default=str))
                file.close()

    @staticmethod
    def load_events(self, events):
        """Load events that are stored in backup events.json"""
        # will need to account for datetime conversion
        pass
