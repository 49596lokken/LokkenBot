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
        if message.mentions[0] == bot.user:
            await message.channel.send(f"The prefix is \"{findprefix(bot, message)}\"")
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, exception):
    await ctx.send(exception.args[0])

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    for guild in bot.guilds:
        me = guild.me
        for text_channel in guild.text_channels:
            
            message_id = text_channel.last_message_id
            message = await text_channel.fetch_message(message_id)
            if message:
                break
        if message:
            await me.edit(nick=f"({findprefix(bot, message)}) {bot.user.name}")

categories = ["games", "useful", "lokkoin", "tcg", "management", "maths"]
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
