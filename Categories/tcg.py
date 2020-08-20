import discord
from discord.ext import commands
import random

class Tcg(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.cards = [chr(i) for i in range(128016, 128170)]
        self.common = [self.cards[i] for i in range(1, 107)]
        self.rare = [self.cards[i] for i in range(127, 153)]
        self.epic = [self.cards[i] for i in range(108, 126)]
        self.legendary = [self.cards[i] for i in [0, 107, 126, 153]]
    

    def get_inventory(self, player:str):
        inventory = None
        f = open("assets/tcg/inventories", "r")
        for line in f:
            if line[:line.index(":")] == player:
                inventory = line[:- 1]
                break
        if not inventory:
            return(None)
        inventory = [int(i) for i in inventory.split(" ")[1:]]
        return([self.cards[i] for i in inventory])


    def is_card(self,card):
        return(card in self.cards)

    @commands.command()
    async def allcards(self, ctx):
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

    def make_pack(self):
        pack = ""
        rarities = []
        for i in range(5):
            rarity_choice = random.randint(1,1200)
            if rarity_choice < 5:
                rarities.append("legendary")
                pack += random.choice(self.legendary)
            elif rarity_choice < 85:
                rarities.append("epic")
                pack += random.choice(self.epic)
            elif rarity_choice < 241:
                rarities.append("rare")
                pack += random.choice(self.rare)
            else:
                rarities.append("common")
                pack += random.choice(self.common)
        return([pack, rarities])

    @commands.command(brief="costs 50 lokkoins for a pack of 5")
    async def pack(self, ctx):
        lokkoin = self.bot.get_cog("lokkoin")
        if not lokkoin:
            await ctx.send("Unable to get lokkoin")
            return
        balance = await lokkoin.get_balance(str(ctx.author.id))
        if not balance:
            await ctx.send("You have either not registered for lokkoin or have no coins")
            return
        if balance < 50:
            await ctx.send("Not enough coins for a pack")
            return
        pack = self.make_pack()
        output = "You got:\n"
        for card in pack[0]:
            output += card[0]
        for rarity in pack[1]:
            output += f"\n{rarity}"
        await ctx.send(output)
        


def setup(bot):
    bot.add_cog(Tcg(bot))