import discord
from discord.ext import commands
from checks import *
import sys

def findprefix(bot, message):
    if not message.guild:
        return("")
    if bot.user.name == "LokkenTestBot":
        default_prefix = "^"
    else:
        default_prefix = "%"
    f = open("prefixes", "r")
    for line in f:
        if line[:line.index(":")] == str(message.guild.id):
            f.close()
            return(line[line.index(":")+1:-1])
    f.close()
    f = open("prefixes", "a")
    f.write(f"{message.guild.id}:{default_prefix}\n")
    f.close()
    return(default_prefix)

bot = commands.Bot(command_prefix=findprefix, case_insensitive=True, help_command=None)

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
categories = ["dos", "c4", "xo", "useful", "lokkoin", "tcg", "management", "maths", "master", "rng", "eh", "lokken", "help", "yahtzee"]
for category in categories:
    try:
        bot.load_extension(f"Categories.{category}")
    except Exception as e:
        print(e)
    
    


@bot.command()
@bot.check(is_creator())
async def reload(ctx, cog_name):
    bot.reload_extension(f"Categories.{cog_name}")
    await ctx.send(f"{cog_name} has been reloaded")


@bot.command()
@bot.check(is_creator())
async def unload(ctx, cog_name):
    bot.remove_cog(cog_name)
    bot.unload_extension(f"Categories.{cog_name}")
    await ctx.send(f"{cog_name} has been unloaded")


@bot.command()
@bot.check(is_creator())
async def load(ctx, cog_name):
    bot.load_extension(f"Categories.{cog_name}")
    await ctx.send(f"{cog_name} has been loaded")







TOKEN = open("token", "r").read()
bot.run(TOKEN)
