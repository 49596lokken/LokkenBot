from discord.ext.commands import check

def is_creator():
    def predicate(ctx):
        return (ctx.author.id in [315845454254571521, 360493765154045952])
    return check(predicate)