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
            with open(self.config_file , "r", encoding="utf-8") as tf:
                self.token = self.__parse_config_line(tf.readline(), "token")
                self.prefix = self.__parse_config_line(tf.readline(), "prefix")
                self.version = self.__parse_config_line(tf.readline(), "version")
                self.owner_ids = self.__parse_config_line(tf.readline(), "owner_ids")
                self.guild = self.__parse_config_line(tf.readline(), "guild")
        except FileNotFoundError:
            print("Config file " + self.config_file  + " could not be found.")
        except ValueError:
            print("Config file improperly formatted.")

    def __parse_config_line(self, line, property_name):
        parsed = line.split("=")
        parsed_value_array = parsed[1].split(",")  # allow for comma-separated values (such as owner ids)

        if len(parsed) != 2:
            raise ValueError
        elif parsed[0] != property_name:
            raise ValueError
        elif len(parsed_value_array) > 1:
            return parsed_value_array
        else:
            return str(parsed[1]).rstrip()