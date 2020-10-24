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
    
    @commands.command(description="Divides a polynomial of any degree by a polynomial of degree 1 e.g. to divide 10x^3+2x^2-5x+1 by x+8, enter 10 2 -5 1 1 8")
    async def polydiv(self, ctx, *coefficients: int):
        coefficients = [i for i in coefficients]
        if len(coefficients) < 5:
            await ctx.send("I can only divide a polynomial of degree 2")
            return
        numerator = coefficients[:-2]
        denominator = coefficients[-2:]
        being_taken = Fraction(0,1)
        answer = []
        for i in numerator[:-1]:
            being_taken = i-being_taken
            answer.append(being_taken/denominator[0])
            being_taken = (being_taken*denominator[1])/denominator[0]
        output = " "
        for i in range(len(numerator)):
            output += f"{numerator[i]}x^{len(numerator)-1-i}+"
        output = output[:-1] + f" Divided by {denominator[0]}x+{denominator[1]} = \n "
        for i in range(len(answer)):
            output += f"{answer[i]}x^{len(answer)-1-i}+"
        output = output.replace("^1+", "+").replace("x^0", "").replace("+-", "-").replace("+1x", "+x").replace("-1x", "-x").replace(" 1x", " x").replace("\n ", "\n")
        await ctx.send(f"{output[:-1]} remainder {numerator[-1]-being_taken}") 

    @commands.command(description="Simplifies a fraction")
    async def simplify(self, ctx, fraction):
        output = fraction[:]
        if not "/" in output:
            await ctx.send("You need to put encode your fraction as  \"a/b\"")
            return
        output = (output[:output.index("/")], output[output.index("/")+1:])
        if output[-1] == "0":
            await ctx.send("You cannot divide by 0")
            return
        for i in output:
            if not i.isdigit:
                await ctx.send(f"{i} is not a number")
                return
        output = Fraction(int(output[0]), int(output[1]))
        await ctx.send(f"The fraction {fraction} is equivelent to {output}")

class Fraction:
    def __init__(self,numerator,denominator):
        cf = hcf(numerator, denominator)
        self.numerator=numerator//cf
        self.denominator=denominator//cf
    
    def __str__(self):
        if self.denominator == 1:
            return(str(self.numerator))
        if self.numerator > 0:
            return(f"({self.numerator}/{self.denominator})")
        return(f"-({abs(self.numerator//1)}/{self.denominator})")
    
    def simplify(self):
        cf = hcf(self.denominator, self.numerator)
        self.numerator, self.denominator = self.numerator//cf, self.denominator//cf
    
    def __mul__(self, other):
        if isinstance(other, int):
            return(Fraction(other*self.numerator, self.denominator))
        return(self.numerator*other.numerator, self.denominator*other.denominator)
    
    __rmul__ = __mul__
    
    def __add__(self,other):
        if isinstance(other, int):
            return(Fraction(other*self.denominator+self.numerator, self.denominator))
        return(Fraction(other.denominator*self.numerator+other.numerator*self.denominator, self.denominator*other.denominator))
    
    __radd__ = __add__

    def __neg__(self):
        return(Fraction(-self.numerator, self.denominator))

    def __sub__(self,other):
        return(self+(-other))
    
    def __rsub__(self,other):
        return(other+-self)

    def __truediv__(self, other):
        if isinstance(other, int):
            return(Fraction(self.numerator, self.denominator*other))
        return(Fraction(self.numerator*other.denominator, other.numerator*self.denominator))
    
    def __rtruediv__(self, other):
        if isinstance(other, int):
            return(Fraction(self.denominator*other, self.numerator))
        return(Fraction(other.numerator*self.denominator, other.numerator*self.denominator))


def hcf(x, y):
    while(y):
        x, y = y, x % y
    return x
a=Fraction(1,2)

    


def setup(bot):
    bot.add_cog(maths(bot))


