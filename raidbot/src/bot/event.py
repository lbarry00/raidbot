import datetime

from event_data import EventData


class Event:
    player_count: int
    activity: str
    type: str
    start_date: datetime
    start_time: datetime
    accepted_players: str
    tentative_players: str
    declined_players: str

    def __init__(self, activity_short_name):
        event_data = EventData("config.json")
        event_data.parse_and_setup()
        event_info = event_data.get_single_event(activity_short_name)
        # initialize event variables
        self.player_count = event_info["player_count"]
        self.activity = event_info["long_name"]
        self.type = event_info["type"]
        self.accepted_players = ""
        self.declined_players = ""
        self.tentative_players = ""
