import discord
from discord.ext import commands
import random
import asyncio
import typing

class Tcg(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.cards = [chr(i) for i in range(128016, 128170)]
        self.common = [self.cards[i] for i in range(1, 107)]
        self.rare = [self.cards[i] for i in range(127, 153)]
        self.epic = [self.cards[i] for i in range(108, 126)]
        self.legendary = [self.cards[i] for i in [0, 107, 126, 153]]
    

    def get_inventory(self, player):
        inventory = None
        f = open("data/tcg/inventories", "r")
        for line in f:
            if line[:line.index(":")] == player:
                inventory = line[:- 1]
                break
        if not inventory:
            return(None)
        inventory = [int(i) for i in inventory.split(" ")[1:]]
        return(inventory)

    def sort_inventory(self, inventory):
        sorted_inventory = [[] for i in range(4)]
        for card in inventory:
            if self.cards[card] in self.common:
                sorted_inventory[0].append(card)
            elif self.cards[card] in self.rare:
                sorted_inventory[1].append(card)
            elif self.cards[card] in self.epic:
                sorted_inventory[2].append(card)
            else:
                sorted_inventory[3].append(card)
        inventory = []
        for i in range(len(sorted_inventory)):
            sorted_inventory[i].sort()
            for card in sorted_inventory[i]:
                inventory.append(card)
        return(inventory)

    def update_inventory(self, player, inventory):
        f = open("data/tcg/inventories", "r")
        all_inventories = f.read().split("\n")[:-1]
        output = ""
        for line_num in range(len(all_inventories)):
            if all_inventories[line_num][:all_inventories[line_num].index(":")] == player:
                all_inventories[line_num] = f"{player}:"
                for card in inventory:
                    all_inventories[line_num] += f" {card}"
            output += all_inventories[line_num]+"\n"
        f=open("data/tcg/inventories", "w")
        f.write(output)
        f.close()

    def add_cards(self, player, cards: list):
        inventory = self.get_inventory(player)
        if inventory==None:
            f=open("data/tcg/inventories", "a")
            f.write(f"{player}:\n")
            inventory = []
            f.close()
        for card in cards:
            inventory.append(card)
        inventory = self.sort_inventory(inventory)
        self.update_inventory(player, inventory)
        

    def remove_cards(self, player, cards: list):
        inventory = self.get_inventory(player)
        for card in cards:
            inventory.remove(card)
            self.update_inventory(player, inventory)

    

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


    @commands.command(description="Shows all of the cards in the game")
    async def allcards(self, ctx):
        e = discord.Embed(title=f"All of the cards in {self.bot.user.name} TCG")
        common, rare, epic, legendary = "", "", "", ""
        for card in self.common:
            common += f"{card} ({self.cards.index(card)})\n"
        for card in self.rare:
            rare += f"{card} ({self.cards.index(card)})\n"
        for card in self.epic:
            epic += f"{card} ({self.cards.index(card)})\n"
        for card in self.legendary:
            legendary += f"{card} ({self.cards.index(card)})\n"
        rarities = {"common":common, "rare":rare, "epic":epic, "legendary":legendary}
        print(len(common))
        for rarity in rarities:
            e.add_field(name=rarity, value=rarities[rarity], inline=True)
        await ctx.send(embed=e)

    @commands.command(brief="costs 50 lokkoins for a pack of 5",description="Gives you a pack of cards")
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
        self.add_cards(str(ctx.author.id), [self.cards.index(card) for card in pack[0]])
        await lokkoin.remove_coins(str(ctx.author.id), 50)

    @commands.command(description="Shows you the inventory of a player (defaults to the author)")
    async def inventory(self, ctx, player: typing.Optional[commands.MemberConverter] = None):
        if not player:
            player = ctx.author
        inventory = self.get_inventory(str(player.id))
        if not inventory:
            await ctx.send(f"{player.display_name} doesn't have any cards")
            return
        inventory = [self.cards[i] for i in inventory]
        e = discord.Embed(title=f"Inventory of {player.name}",description=f"{len(inventory)} cards")
        common, rare, epic, legendary = "", "", "", ""
        occurences = 0
        last_card = inventory[0]
        num_of_each = [int(i==0) for i in range(4)]
        for card in inventory:
            if card in self.common:
                if card == last_card:
                    occurences += 1
                else:
                    num_of_each[0] += 1
                    common += f"{occurences}\u00d7{last_card}({self.cards.index(last_card)})\n"
                    occurences = 1
                    last_card = card
            elif card in self.rare:
                if card == last_card:
                    occurences += 1
                else:
                    num_of_each[1] += 1
                    rare += f"{occurences}\u00d7{last_card}({self.cards.index(last_card)})\n"
                    occurences = 1
                    last_card = card
            elif card in self.epic:
                if card == last_card:
                    occurences += 1
                else:
                    num_of_each[2] += 1
                    epic += f"{occurences}\u00d7{last_card}({self.cards.index(last_card)})\n"
                    occurences = 1
                    last_card = card
            else:
                if card == last_card:
                    occurences += 1
                else:
                    num_of_each[3] += 1
                    legendary += f"{occurences}\u00d7{last_card}({self.cards.index(last_card)})\n"
                    occurences = 1
                    last_card = card
        
        if last_card in self.common:
            common += f"{occurences}\u00d7{last_card}({self.cards.index(last_card)})\n"
        elif last_card in self.rare:
            rare += f"{occurences}\u00d7{last_card}({self.cards.index(last_card)})\n"
            common += rare[:rare.index("\n")]
            rare = rare[rare.index("\n")+1:]
        elif last_card in self.epic:
            epic += f"{occurences}\u00d7{last_card}({self.cards.index(last_card)})\n"
            common += rare[:rare.index("\n")]
            rare = rare[rare.index("\n")+1:]
            rare += epic[:epic.index("\n")]
            epic = epic[epic.index("\n")+1:]
        else:
            legendary += f"{occurences}\u00d7{last_card}({self.cards.index(last_card)})\n"
            common += rare[:rare.index("\n")]
            rare = rare[rare.index("\n")+1:]
            rare += epic[:epic.index("\n")]
            epic = epic[epic.index("\n")+1:]
            epic += legendary[:legendary.index("\n")]
            legendary = legendary[legendary.index("\n")+1:]

    
        e.add_field(name=f"common {num_of_each[0]}/{len(self.common)}", value=common+int(num_of_each[0]==0)*"No cards", inline=True)
        e.add_field(name=f"rare {num_of_each[1]}/{len(self.rare)}",value=rare+int(num_of_each[1]==0)*"No cards",inline=True)
        e.add_field(name=f"epic {num_of_each[2]}/{len(self.epic)}",value=epic+int(num_of_each[2]==0)*"No cards",inline=True)
        e.add_field(name=f"legandary {num_of_each[3]}/{len(self.legendary)}",value=legendary+int(num_of_each[3]==0)*"No cards",inline=True)
            


        await ctx.send(embed=e)

    @commands.command(description="Syntax - trade (things you're giving separated by spaces) for (things you're taking separated by spaces)\nTo trade an emoji use its id\nFor lokkoin payments, type \"l\" followed by the number of lokkoins")
    async def trade(self, ctx, friend: commands.MemberConverter, *args):
        args = [arg.lower() for arg in args]
        if not "for" in args:
            await ctx.send("You need to include \"for\" as one of the arguments")
            return
        giving = args[:args.index("for")]
        getting = args[args.index("for")+1:]
        lokkoin_transaction = []
        lokkoin = self.bot.get_cog("lokkoin")
        inventory = self.get_inventory(str(ctx.author.id))[:]
        for card in giving:
            if not card.isdigit():
                if not card[1:].isdigit():
                    await ctx.send("Please use a number for this")
                    return
                card = card[1:]
                if lokkoin_transaction:
                    await ctx.send("There is already lokkoin in this trade. Cancelling")
                    return
                lokkoin_transaction = [int(card), str(ctx.author.id)]
                balance = await lokkoin.get_balance(str(ctx.author.id))
                if not balance:
                    await ctx.send("You have no balance try register or make more money")
                    return
                if balance < int(card):
                    await ctx.send("You don't have that much money... trade cancelled")
                    return
                giving.remove(f"l{card}")
                break
            card = int(card) 
            if not card in [i for i in range(len(self.cards))]:
                await ctx.send(f"{card} is not a card. Cancelling trade")
                return
            if not card in inventory:
                await ctx.send(f"You do not have the card {self.cards[card]} in your inventory")
                return
            inventory.remove(card)
        inventory = self.get_inventory(str(friend.id))[:]
        for card in getting:
            if not card.isdigit():
                if not card[1:].isdigit():
                    await ctx.send("Please use a number for this")
                    return
                card = card[1:]
                if lokkoin_transaction:
                    await ctx.send("There is already lokkoin in this trade")
                    return
                lokkoin_transaction = [int(card), str(ctx.author.id)]
                balance = await lokkoin.get_balance(str(friend.id))
                if not balance:
                    await ctx.send("Your has no balance. They should try register or make more money")
                    return
                if balance < int(card):
                    await ctx.send("Your friend doesn't have that much money... trade cancelled")
                    return
                getting.remove(f"l{card}")
                break
            card = int(card)
            if not card in [i for i in range(len(self.cards))]:
                await ctx.send(f"{card} is not a card. Cancelling trade")
                return
            if not card in inventory:
                await ctx.send(f"Your friend does not have the card {self.cards[card]} in their inventory")
                return
            inventory.remove(card)

        output = ""
        for arg in args:
            if arg.isdigit():
                output += self.cards[int(arg)]
            elif arg.startswith("l"):
                output += f" {arg[1:]} lokkoins "
            else:
                output += arg
        confirmation = await friend.send(f"Player {ctx.author.name}#{ctx.author.discriminator} has requested a trade with you. They want to give you {output}\nTo confirm this trade, react with a \u2705")
        await confirmation.add_reaction("\u2705")
        confirmation = await friend.fetch_message(confirmation.id)
        def check(reaction, user):
            return(str(reaction.emoji) == "\u2705" and user == friend and reaction.message.id==confirmation.id)
        try:
            await self.bot.wait_for("reaction_add", check=check, timeout=20.0)
            if lokkoin_transaction:
                if lokkoin_transaction[1] == str(ctx.author.id):
                    await lokkoin.remove_coins(str(ctx.author.id), lokkoin_transaction[0])
                    await lokkoin.add_coins(str(friend.id), lokkoin_transaction[0])
                else:
                    await lokkoin.remove_coins(str(friend.id), lokkoin_transaction[0])
                    await lokkoin.add_coins(str(ctx.author.id), lokkoin_transaction[0])
            giving = [int(card) for card in giving]
            getting = [int(card) for card in getting]
            self.remove_cards(str(ctx.author.id), giving)
            self.add_cards(str(friend.id), giving)
            self.remove_cards(str(friend.id), getting)
            self.add_cards(str(ctx.author.id), getting)
            await ctx.send("Done - The trade went through")
        except asyncio.TimeoutError:
            await ctx.send("Your friend didn't react in time.")



def setup(bot):
    bot.add_cog(Tcg(bot))
