from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog, command

from event import Event

# TODO: add editing of fields after reaction. Write the events to an external file in case bot crashes.

# Unicode for emojis to use in lfg command
green_check_mark, red_x, question_mark = "\u2705", "\u274C", "\u2753"
# List of emojis
lfg_reactions = [green_check_mark, red_x, question_mark]
# List of events to check for
game_events_list = ["dsc", "lw", "gos", "trials", "comp"]


class Commands(Cog):

    def __init__(self, bot):
        self.bot = bot
        # store our events in this dict.
        self.events = {}

    @Cog.listener()
    async def on_ready(self):
        self.bot.get_channel(807731959400366142)

    @command(name="lfg")
    async def lfg(self, ctx, activity_short_name):
        if activity_short_name and activity_short_name.strip() and activity_short_name in game_events_list:
            # TODO: correct date time from now to argument parsing
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M")
            # instantiate event, then use for embed fields
            new_event = Event(activity_short_name)
            embed = Embed(title=new_event.activity, description=str(date_time), color=0x8000ff)
            embed.add_field(name="Players Needed ", value=str(new_event.player_count), inline=False)
            embed.add_field(name="Accepted players " + green_check_mark, value=ctx.author.name, inline=False)
            new_event.accepted_players += ctx.author.name
            embed.add_field(name="Declined players " + red_x, value=chr(173), inline=False)
            embed.add_field(name="Tentative players " + question_mark, value=chr(173), inline=False)
            message = await ctx.send(embed=embed)
            # add reactions to embed
            for emoji in lfg_reactions[:len(lfg_reactions)]:
                await message.add_reaction(emoji)

            # add to dict with key: message.id, val: event
            self.events[message.id] = new_event
        else:
            await ctx.send("Unrecognized activity in lfg command. Please use " + str(game_events_list))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.events.keys():
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            # remove reaction if not the bot and member has reacted already and they used something else
            for reaction in message.reactions:
                if (not payload.member.bot
                        and payload.member in await reaction.users().flatten()
                        and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)

                elif not payload.member.bot and reaction.emoji == green_check_mark:
                    pass

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        pass


def setup(bot):
    bot.add_cog(Commands(bot))
