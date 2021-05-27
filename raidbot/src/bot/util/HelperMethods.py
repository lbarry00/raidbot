import pytz

from discord import Embed
from discord.utils import get

# Unicode for emojis to use in lfg command
green_check_mark, red_x, question_mark = "✅", "❌", "❓"


class HelperMethods:

    @staticmethod
    async def update_embed(message, events):
        """Update the embed fields based on list changing in updateLists()"""
        event = events[message.id]

        # process lists of players
        accepted_string = await HelperMethods.process_list(event.accepted_players)
        declined_string = await HelperMethods.process_list(event.declined_players)
        tentative_string = await HelperMethods.process_list(event.tentative_players)

        embed = Embed(title=event.activity, description="Reminder ID = " + str(event.id), timestamp=event.start_time,
                      color=0x8000ff)
        embed.add_field(name="Players Needed ", value=str(event.player_count), inline=False)
        embed.add_field(name="Accepted Players " + green_check_mark, value=accepted_string, inline=False)
        embed.add_field(name="Declined players " + red_x, value=declined_string, inline=False)
        embed.add_field(name="Tentative players " + question_mark, value=tentative_string, inline=False)
        await message.edit(embed=embed)

    @staticmethod
    async def update_lists(payload, message, add_remove, events):
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
        await HelperMethods.update_embed(message, events)

    @staticmethod
    async def delete_previous_reaction(payload, message):
        """Users should only be able to vote once. If new reaction added remove any previous reaction."""
        for reaction in message.reactions[:len(message.reactions)]:
            if (payload.member in await reaction.users().flatten()
                    and reaction.emoji != payload.emoji.name):
                await message.remove_reaction(reaction.emoji, payload.member)

    @staticmethod
    async def process_list(player_list):
        """For embeds, process lists of players stored in event class so it displays nicely in embed"""
        if not player_list:
            return chr(173)
        else:
            list_as_string = "\n".join(f"{player}" for player in player_list)
            return list_as_string

    @staticmethod
    async def get_user_timezone(ctx, time):
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
