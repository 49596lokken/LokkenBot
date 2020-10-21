import discord
from discord.ext import commands
import sys
import os
intents = discord.Intents.default()
intents.members = True

def findprefix(bot, message):
    if not message.guild:
        f = open("data/prefixes-dm", "r")
        for line in f:
            if line[:line.index(":")] == str(message.author .id):
                f.close()
                return(line[line.index(":")+1:-1])
        f.close()
        f = open("data/prefixes-dm", "a")
        f.write(f"{message.author.id}:-\n")
        f.close()
        return("-")

    if bot.user.name == "LokkenTestBot":
        default_prefix = "^"
    else:
        default_prefix = "%"
    f = open("data/prefixes", "r")
    for line in f:
        if line[:line.index(":")] == str(message.guild.id):
            f.close()
            return(line[line.index(":")+1:-1])
    f.close()
    f = open("data/prefixes", "a")
    f.write(f"{message.guild.id}:{default_prefix}\n")
    f.close()
    return(default_prefix)

bot = commands.Bot(command_prefix=findprefix, case_insensitive=True, help_command=None,intents=intents)

@bot.event
async def on_message(message):
    if len(message.mentions) == 1:
        if message.mentions[0] == bot.user and message.content.index("<") == 0 and message.content.index(">") == len(message.content)-1 and not ("<" in message.content[1:]):
            await message.channel.send(f"The prefix is \"{findprefix(bot, message)}\"")
            return
    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    print(f"On discord.py version {discord.__version__} in python {sys.version}")
    await bot.change_presence(activity=discord.Game("ping me for prefix"))
categories = os.listdir("Categories")
for category in categories:
    if category.endswith(".py"):
        try:
            bot.load_extension(f"Categories.{category[:-3]}")
        except Exception as e:
            print(e)

@commands.check
async def is_me(ctx):
    return(ctx.author.id == 360493765154045952)


@bot.command(description="Reloads a cog")
@is_me
async def reload(ctx, cog_name):
    bot.reload_extension(f"Categories.{cog_name}")
    await ctx.send(f"{cog_name} has been reloaded")


@bot.command(description="Unloads a Cog")
@is_me
async def unload(ctx, cog_name):
    bot.remove_cog(cog_name)
    bot.unload_extension(f"Categories.{cog_name}")
    await ctx.send(f"{cog_name} has been unloaded")


@bot.command(description="Loads a Cog")
@is_me
async def load(ctx, cog_name):
    bot.load_extension(f"Categories.{cog_name}")
    await ctx.send(f"{cog_name} has been loaded")



TOKEN = open("token", "r").read()
bot.run(TOKEN)
