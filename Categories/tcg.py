import discord
from discord.ext import commands


class Tcg(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.common = [chr(i) for i in range(128017, 128080)]
        self.rare = [chr(i) for i in range(128081, 128141)]
        self.epic = [chr(i) for i in range(128143, 128170)]
        self.legendary = [chr(i) for i in [128016, 128081, 128142, 128169]]

    @commands.command()
    async def tcg_cards(self, ctx):
        output = ""
        output += "common\n"
        for card in self.common:
            output += card
        output += "\nrare\n"
        for card in self.rare:
            output += card
        output += "\nepic\n"
        for card in self.epic:
            output += card
        output += "\nlegendary\n"
        for card in self.legendary:
            output += card
        await ctx.send(output)
        

    @commands.command()
    async def pack(self, ctx):
        ...


def setup(bot):
    bot.add_cog(Tcg(bot))