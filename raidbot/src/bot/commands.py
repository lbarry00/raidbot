from datetime import datetime

import pytz
from discord import Embed
from discord.ext.commands import Cog, command, MissingRequiredArgument
from discord.utils import get

from event import Event

# Unicode for emojis to use in lfg command
green_check_mark, red_x, question_mark = "✅", "❌", "❓"
# List of emojis
lfg_reactions = [green_check_mark, red_x, question_mark]
# List of events to check for
game_events_list = ["ce", "dsc", "gos", "kf", "lw", "vog", "wotm", "comp", "ib", "trials"]
# List of events with full names
game_events_list_long = ["Crota's End", "Deep Stone Crypt", "Garden of Salvation", "Kings Fall", "Last Wish",
                         "Vault of Glass", "Wrath of the Machine", "Competitive", "Iron Banner", "Trials of Osiris"]
# Class dict of events
events = {}


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.bot.get_channel(807731959400366142)

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

            new_time = await self.get_user_timezone(ctx, date_time)
            # if new_time is null, user did not have timezone role, don't proceed
            if new_time:
                # instantiate event, then use for embed fields
                new_event = Event(activity_short_name)
                embed = Embed(title=new_event.activity, timestamp=new_time, color=0x8000ff)
                embed.add_field(name="Players Needed ", value=str(new_event.player_count), inline=False)
                embed.add_field(name="Accepted players " + green_check_mark, value=chr(173), inline=False)
                embed.add_field(name="Declined players " + red_x, value=chr(173), inline=False)
                embed.add_field(name="Tentative players " + question_mark, value=chr(173), inline=False)
                message = await ctx.send(embed=embed)

                for emoji in lfg_reactions[:len(lfg_reactions)]:
                    await message.add_reaction(emoji)

                # add to dict with key: message.id, val: event
                events[message.id] = new_event
        else:
            await ctx.send("Unrecognized activity in lfg command. Please use " + str(game_events_list))

    @lfg.error
    async def lfg_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Invalid argument detected. Use !help <command> to see proper format.")
        else:
            raise error

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Remove reactions that are not preset. For every expected reaction, update the embed."""
        if payload.message_id in events.keys():
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            if not payload.member.bot and payload.emoji.name not in lfg_reactions:
                await message.remove_reaction(payload.emoji, payload.member)

            elif not payload.member.bot and payload.emoji.name in lfg_reactions:
                await self.delete_previous_reaction(payload, message)
                await self.update_lists(payload, message, True)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Ignore removals that are not preset. For every expected reaction removal update the embed."""
        if payload.message_id in events.keys():
            if payload.emoji.name not in lfg_reactions:
                return
            elif payload.emoji.name in lfg_reactions:
                message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await self.update_lists(payload, message, False)

    async def update_lists(self, payload, message, add_remove):
        """Update the event objects lists of players depending on reaction choice, then update the embed"""
        event = events[message.id]
        # for remove methods, no member passed, instantiating member from payload
        member = await message.guild.fetch_member(payload.user_id)
        if add_remove:
            if payload.emoji.name == green_check_mark:
                event.accepted_players.append(member.name)
            elif payload.emoji.name == red_x:
                event.declined_players.append(member.name)
            elif payload.emoji.name == question_mark:
                event.tentative_players.append(member.name)
        else:
            if payload.emoji.name == green_check_mark:
                event.accepted_players.remove(member.name)
            elif payload.emoji.name == red_x:
                event.declined_players.remove(member.name)
            elif payload.emoji.name == question_mark:
                event.tentative_players.remove(member.name)
        await self.update_embed(message)

    async def update_embed(self, message):
        """Update the embed fields based on list changing in updateLists()"""
        event = events[message.id]

        # process lists of players
        accepted_string = await self.process_list(event.accepted_players)
        declined_string = await self.process_list(event.declined_players)
        tentative_string = await self.process_list(event.tentative_players)

        embed = Embed(title=event.activity, description="Updated description", color=0x8000ff)
        embed.add_field(name="Players Needed ", value=str(event.player_count), inline=False)
        embed.add_field(name="Accepted Players " + green_check_mark, value=accepted_string, inline=False)
        embed.add_field(name="Declined players " + red_x, value=declined_string, inline=False)
        embed.add_field(name="Tentative players " + question_mark, value=tentative_string, inline=False)
        await message.edit(embed=embed)

    async def delete_previous_reaction(self, payload, message):
        """Users should only be able to vote once. If new reaction added remove any previous reaction."""
        for reaction in message.reactions[:len(message.reactions)]:
            if (payload.member in await reaction.users().flatten()
                    and reaction.emoji != payload.emoji.name):
                await message.remove_reaction(reaction.emoji, payload.member)

    async def process_list(self, player_list):
        """For embeds, process lists of players stored in event class so it displays nicely in embed"""
        if not player_list:
            return chr(173)
        else:
            list_as_string = "\n".join(f"{player}" for player in player_list)
            return list_as_string

    async def get_user_timezone(self, ctx, time):
        """Get user's timezone from timezone role and convert given time to UTC.
         Giving embed UTC timestamp updates to everyone's appropriate time"""
        author = ctx.message.author
        roles = ctx.message.guild.roles
        eastern = get(roles, name="ET")
        central = get(roles, name="CT")
        pacific = get(roles, name="PT")
        hawaii = get(roles, name="HT")
        eastern_european = get(roles, name="EET")

        if eastern in author.roles:
            eastern = pytz.timezone("America/New_York")
            time = eastern.localize(time)
        elif central in author.roles:
            central = pytz.timezone("America/Chicago")
            time = central.localize(time)
        elif pacific in author.roles:
            pacific = pytz.timezone("America/Los_Angeles")
            time = pacific.localize(time)
        elif hawaii in author.roles:
            hawaii = pytz.timezone("Pacific/Honolulu")
            time = hawaii.localize(time)
        elif eastern_european in author.roles:
            bucharest = pytz.timezone("Europe/Bucharest")
            time = bucharest.localize(time)
        else:
            await ctx.send(
                "You do not have any timezone roles, please assign your appropriate timezone role and retry.")
            return

        time = time.astimezone(pytz.UTC)
        return time

    async def print_message(self):
        channel = self.bot.get_channel(807731959400366142)
        await channel.send("Message test!")


def setup(bot):
    bot.add_cog(Commands(bot))
