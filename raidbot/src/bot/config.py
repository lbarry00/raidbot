import json

class Config:

    def __init__(self):
        self.token = None
        self.prefix = None
        self.version = None
        self.owner_ids = []
        self.guild = None

        self.config_file = None

    def __init__(self, config_file):
        self.token = None
        self.prefix = None
        self.version = None
        self.owner_ids = []
        self.guild = None

        self.config_file = config_file

    def setup_config(self):
        if self.config_file is None:
            print("Config file not set.")
            exit(1)

        try:
            with open(self.config_file, "r", encoding="utf-8") as tf:
                data = json.load(tf)

                self.token = data["token"]
                self.prefix = data["prefix"].rstrip()
                self.version = data["version"]
                self.owner_ids = data["owner_ids"]
                self.guild = data["guild"]
        except FileNotFoundError:
            print("Config file " + self.config_file  + " could not be found.")
            exit(1)
        except KeyError as e:
            print("Config file improperly formatted.")
            print(e)
            exit(1)