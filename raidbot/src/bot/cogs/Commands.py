from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog, command, MissingRequiredArgument

from raidbot.src.event.Event import Event
from raidbot.src.bot.util.HelperMethods import HelperMethods

# Unicode for emojis to use in lfg command
green_check_mark, red_x, question_mark = "✅", "❌", "❓"
# List of emojis
lfg_reactions = [green_check_mark, red_x, question_mark]
# List of events to check for
game_events_list = ["ce", "dsc", "gos", "kf", "lw", "vog", "wotm", "comp", "ib", "trials", "nf"]
# List of events with full names
game_events_list_long = ["Crota's End", "Deep Stone Crypt", "Garden of Salvation", "Kings Fall", "Last Wish",
                         "Vault of Glass", "Wrath of the Machine", "Competitive", "Iron Banner", "Trials of Osiris",
                         "Nightfalls"]
# Class dict of events
events = {}


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="lfg",
        help="Schedule a raid using the above format. \n\n" +
             "Short names: " + ', '.join(game_events_list) + "\n"
                                                             "Time format needed is mm-dd-yyyy hh:mm AM/PM \n\n" +
             "Full names: " + ', '.join(game_events_list_long))
    async def lfg(self, ctx, activity_short_name, *, time):
        if activity_short_name and activity_short_name.strip() and activity_short_name in game_events_list:
            try:
                date_time = datetime.strptime(time, "%m/%d/%Y %I:%M %p")
            except ValueError:
                await ctx.send("Unrecognized time in lfg command. Please use '!help lfg' to learn more")
                return

            new_time = await HelperMethods.get_user_timezone(ctx, date_time)
            # if new_time is null, user did not have timezone role, don't proceed
            if new_time:
                # instantiate event, then use for embed fields
                new_event = Event(activity_short_name)
                # setup initial event embed to be edited, because we need message id set first.
                embed = Embed(title=new_event.activity,
                              description="",
                              timestamp=new_time,
                              color=0x8000ff)
                message = await ctx.send(embed=embed)
                new_event.id = message.id
                embed = Embed(title=new_event.activity,
                              description="Reminder ID = " + str(new_event.id),
                              timestamp=new_time,
                              color=0x8000ff)
                embed.add_field(name="Players Needed ", value=str(new_event.player_count), inline=False)
                embed.add_field(name="Accepted players " + green_check_mark, value=chr(173), inline=False)
                embed.add_field(name="Declined players " + red_x, value=chr(173), inline=False)
                embed.add_field(name="Tentative players " + question_mark, value=chr(173), inline=False)
                await message.edit(embed=embed)
                # append reactions to message
                for emoji in lfg_reactions[:len(lfg_reactions)]:
                    await message.add_reaction(emoji)
                # pin the message
                # TODO: uncomment this once event listener is in place to remove pin once complete await message.pin()
                new_event.start_time = new_time
                # add to dict with key: message.id, val: event
                events[new_event.id] = new_event
                # send to json backup
                Event.backup_events(new_event)

        else:
            await ctx.send("Unrecognized activity in lfg command. Please use " + str(game_events_list))

    @lfg.error
    async def lfg_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Invalid argument detected. Use !help <command> to see proper format.")
        else:
            raise error

    @command(name="remind", help="Remind tentative or accepted members about an event")
    async def remind(self, ctx, event_id: str):
        # clean input
        clean_event_id = event_id.strip()
        int_event_id = int(clean_event_id)
        # get event
        if int_event_id in events:
            event = events[int_event_id]
            participants = event.accepted_players + event.tentative_players
            if len(participants) == 0:
                await ctx.send(
                    ctx.message.author.mention + " there is no one planned to run " + event.activity +
                    " later. See if someone wants to join!")

            elif len(participants) == 1 and ctx.message.author.name in participants:
                await ctx.send(
                    ctx.message.author.mention + " you are the only one planning to run " + event.activity +
                    " later. See if someone wants to join!")

            else:
                list_as_string = " ".join(f"{player}" for player in participants)
                await ctx.send(
                    ctx.message.author.mention + " is reminding " + list_as_string + " about running " +
                    event.activity + " later!")
        else:
            await ctx.send("Invalid id, please retry")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Remove reactions that are not preset. For every expected reaction, update the embed."""
        if payload.message_id in events.keys():
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            if not payload.member.bot and payload.emoji.name not in lfg_reactions:
                await message.remove_reaction(payload.emoji, payload.member)

            elif not payload.member.bot and payload.emoji.name in lfg_reactions:
                await HelperMethods.delete_previous_reaction(payload, message)
                await HelperMethods.update_lists(payload, message, True, events)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Ignore removals that are not preset. For every expected reaction removal update the embed."""
        if payload.message_id in events.keys():
            if payload.emoji.name not in lfg_reactions:
                return
            elif payload.emoji.name in lfg_reactions:
                message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await HelperMethods.update_lists(payload, message, False, events)


def setup(bot):
    bot.add_cog(Commands(bot))
