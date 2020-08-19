import discord
from discord.ext import commands
from checks import *

def findprefix(bot, message):
    if not message.guild:
        return("")
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
async def on_ready():
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    categories = ["games", "useful", "lokkoin"]
    for category in categories:
        try:
            bot.load_extension(f"Categories.{category}")
        except Exception as e:
            print(e)
    
    for guild in bot.guilds:
        me = guild.me
        for text_channel in guild.text_channels:
            
            message_id = text_channel.last_message_id
            message = await text_channel.fetch_message(message_id)
            if message:
                break
        if message:
            await me.edit(nick=f"({findprefix(bot, message)}) LokkenTestBot")


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



async def on_command_error(ctx, error):
    await ctx.send(str(error))
    print(error)



TOKEN = open("token", "r").read()
bot.run(TOKEN)
