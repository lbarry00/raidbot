import json


class EventData:

    def __init__(self, config_file):
        self.event_data = None
        self.config_file = config_file

    def parse_and_setup(self):
        if self.config_file is None:
            print("Config file not set.")
            exit(1)

        try:
            with open(self.config_file, "r", encoding="utf-8") as tf:
                data = json.load(tf)
                self.event_data = data["event_data"]

        except FileNotFoundError:
            print("Event Config file " + self.config_file  + " could not be found.")
            exit(1)

        except KeyError as e:
            print("Event Config file improperly formatted.")
            print(e)
            exit(1)

    def check_event_exists(self, event_short_name):
        if self.event_data[event_short_name] is not None:
            return True
        else:
            return False

    def get_single_event(self, event_short_name):
        return self.event_data[event_short_name]