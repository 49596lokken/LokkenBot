from discord.ext.commands import check

def is_creator():
    def predicate(ctx):
        return (ctx.author.id in [360493765154045952])
    return check(predicate)