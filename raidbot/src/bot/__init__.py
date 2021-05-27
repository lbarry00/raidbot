from discord.ext.commands import Bot

from raidbot.src.bot.config.BotConfig import BotConfig
from EventData import EventData


class Client(Bot):
    def __init__(self, config):
        self.TOKEN = config.token,
        self.prefix = config.prefix
        self.owner_ids = config.owner_ids
        self.guild = config.guild

        self.ready = False

        super().__init__(command_prefix=config.prefix, owner_ids=config.owner_ids)

    def run(self):
        print("Running bot with the following settings:")
        print("Prefix: " + self.prefix)
        print("Owner IDs: " + ", ".join(self.owner_ids))
        print("Guild: " + self.guild)
        print("--------------------")

        self.TOKEN = config.token
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Bot connected")

    async def on_disconnect(self):
        print("Bot disconnected")

    async def on_ready(self):
        if not self.ready:
            self.ready = True
        else:
            print("Bot reconnected")

    async def on_message(self, message):
        await self.process_commands(message)


config = BotConfig("config/config.json")
config.parse_and_setup()

event_data = EventData("config/config.json")
event_data.parse_and_setup()

if config.token is not None:
    client = Client(config)
    client.load_extension('cogs.Commands')
    client.run()
else:
    print("Something went wrong with config parsing. Exiting...")
    exit(1)