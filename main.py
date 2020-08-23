import discord
from discord.ext import commands
from checks import *

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

bot = commands.Bot(command_prefix=findprefix, case_insensitive=True)

@bot.event
async def on_message(message):
    if len(message.raw_mentions) == 1:
        if message.mentions[0] == bot.user and len(message.content) == len(bot.user.mention)+1:
            await message.channel.send(f"The prefix is \"{findprefix(bot, message)}\"")
    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    await bot.change_presence(activity=discord.Game("ping me for prefix"))
categories = ["dos", "c4", "xo", "useful", "lokkoin", "tcg", "management", "maths", "master", "rng", "eh"]
for category in categories:
    try:
        bot.load_extension(f"Categories.{category}")
    except Exception as e:
        print(e)
    
    


@bot.command()
@bot.check(is_creator())
async def reload(ctx, cog_name):
    try:
        bot.reload_extension(f"Categories.{cog_name}")
        await ctx.send(f"{cog_name} has been reloaded")
    except Exception as e:
        await ctx.send(e)

@bot.command()
@bot.check(is_creator())
async def unload(ctx, cog_name):
    try:
        bot.remove_cog(cog_name)
        bot.unload_extension(f"Categories.{cog_name}")
        await ctx.send(f"{cog_name} has been unloaded")
    except Exception as e:
        await ctx.send(e)

@bot.command()
@bot.check(is_creator())
async def load(ctx, cog_name):
    try:
        bot.load_extension(f"Categories.{cog_name}")
        await ctx.send(f"{cog_name} has been loaded")
    except Exception as e:
        await ctx.send(e)







TOKEN = open("token", "r").read()
bot.run(TOKEN)
