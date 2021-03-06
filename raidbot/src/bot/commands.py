from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog, command

from event import Event

# TODO: add editing of fields after reaction. Write the events to an external file in case bot crashes.

# Unicode for emojis to use in lfg command
green_check_mark, red_x, question_mark = "✅", "❌", "❓"
# List of emojis
lfg_reactions = [green_check_mark, red_x, question_mark]
# List of events to check for
game_events_list = ["ce", "dsc", "gos", "kf", "lw", "vog", "wotm", "comp", "ib", "trials"]
# Class dict of events
events = {}


class Commands(Cog):

    def __init__(self, bot):
        self.bot = bot

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

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Remove reactions that are not preset. For every expected reaction, update the embed."""
        if payload.message_id in events.keys():
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            if not payload.member.bot and payload.emoji.name not in lfg_reactions:
                await message.remove_reaction(payload.emoji, payload.member)

            elif not payload.member.bot and payload.emoji.name in lfg_reactions:
                await self.deletePreviousReaction(payload, message)
                await self.updateLists(payload, message, True)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Ignore removals that are not preset. For every expected reaction removal update the embed."""
        if payload.message_id in events.keys():
            if payload.emoji.name not in lfg_reactions:
                return
            elif payload.emoji.name in lfg_reactions:
                message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await self.updateLists(payload, message, False)

    async def updateLists(self, payload, message, add_remove):
        """Update the event objects lists of players depending on reaction choice, then update the embed"""
        event = events[message.id]
        # for remove methods, no member passed, instantiating member from payload
        member = await message.guild.fetch_member(payload.user_id)
        if (add_remove):
            if (payload.emoji.name == green_check_mark):
                event.accepted_players.append(member.name)
            elif (payload.emoji.name == red_x):
                event.declined_players.append(member.name)
            elif (payload.emoji.name == question_mark):
                event.tentative_players.append(member.name)
        else:
            if (payload.emoji.name == green_check_mark):
                event.accepted_players.remove(member.name)
            elif (payload.emoji.name == red_x):
                event.declined_players.remove(member.name)
            elif (payload.emoji.name == question_mark):
                event.tentative_players.remove(member.name)
        await self.updateEmbed(message)

    async def updateEmbed(self, message):
        """Update the embed fields based on list changing in updateLists()"""
        event = events[message.id]
        embed = Embed(title=event.activity, description="Updated description", color=0x8000ff)
        embed.add_field(name="Players Needed ", value=str(event.player_count), inline=False)
        embed.add_field(name="Accepted players " + green_check_mark, value=event.accepted_players, inline=False)
        embed.add_field(name="Declined players " + red_x, value=event.declined_players, inline=False)
        embed.add_field(name="Tentative players " + question_mark, value=event.tentative_players, inline=False)
        await message.edit(embed=embed)

    async def deletePreviousReaction(self, payload, message):
        """Users should only be able to vote once. If new reaction added remove any previous reaction."""
        for reaction in message.reactions[:len(message.reactions)]:
            if (payload.member in await reaction.users().flatten()
                    and reaction.emoji != payload.emoji.name):
                await message.remove_reaction(reaction.emoji, payload.member)


def setup(bot):
    bot.add_cog(Commands(bot))
