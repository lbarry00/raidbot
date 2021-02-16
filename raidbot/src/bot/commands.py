from discord import Embed
from discord.ext.commands import Cog, command


class Commands(Cog):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(807731959400366142)
       # await channel.send("I've awoken! Hello from cogs in commands.py")

    @command(name="lfg")
    async def lfg(self, ctx):
        embed = Embed(title="Last Wish", description="Go kill Riven", color=0x8000ff)
        embed.add_field(name="Participants", value="6", inline=True)
        embed.add_field(name="Player Name", value=ctx.author.name, inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Commands(bot))