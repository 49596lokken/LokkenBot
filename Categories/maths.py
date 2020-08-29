import discord
from discord.ext import commands
import praw
import aiohttp
import random
import os

class maths(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        f=open("reddit", "r")
        reddit_details = f.read().split("\n")
        self.reddit = praw.Reddit(username=reddit_details[0],password=reddit_details[1],client_secret=reddit_details[2],client_id=reddit_details[3],user_agent="PrawTut")
        f.close()



    @commands.command(description="Sends a mathematical meme to the channel")
    async def mathsmeme(self, ctx):
        subreddit = self.reddit.subreddit("mathmemes")
        memes = list(subreddit.new(limit=15))
        for submission in memes:
            if submission.over_18 or submission.stickied or submission.url.startswith("https://v.redd.it"):
                memes.remove(submission)
        submission = random.choice(memes)
        if submission.is_self:
            e = discord.Embed(title=submission.title, description=submission.selftext)
            await ctx.send(embed=e)
            return
        url = submission.url
        file_extension = url.split(".")[-1]
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    with open(f"meme.{file_extension}", "wb") as f:
                        f.write(await r.content.read())
                    await ctx.send(submission.title, file=discord.File(f"meme.{file_extension}"))
                    os.remove(f"meme.{file_extension}")
    
    @commands.command(description="Sends a specified number of digits to the channel")
    async def pi(self, ctx, digits: int=50):
        f = open("data/maths/pi.txt", "r")
        content = f.read()
        if digits > len(content):
            await ctx.send("Too many digits")
            return
        await ctx.send(f"3.{content[:digits]}")
    

    
        





def setup(bot):
    bot.add_cog(maths(bot))