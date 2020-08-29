import discord
from discord.ext import commands


class none(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.command(name="help", brief="shows this message")
    async def help_command(self, ctx, *request):
        request = [i.lower() for i in request]
        categories = {"none":[]}
        for command in self.bot.all_commands.values():
            cog = command.cog
            if not cog:
                categories["none"].append(command)
            elif cog.qualified_name.lower() in categories:
                categories[cog.qualified_name.lower()].append(command)
            else:
                categories[cog.qualified_name.lower()] = [command]
        if len(request) != 0:
            if request[0] in categories:
                description = ""
                for command in categories[request[0]]:
                    try:
                        checks = command.checks
                        if [check(ctx) for check in checks] == [True for check in checks]:
                            if command.brief:
                                description += f"{command.name} - {command.brief}\n"
                            else:
                                description += f"{command.name}\n"
                    except commands.CommandError:
                        pass
                if description:
                    e = discord.Embed(title=f"{self.bot.user.name} help for {request[0]} category", description=description)
                    e.set_footer(text=f"You can also try {ctx.prefix}help <command> for help on a command")
                    await ctx.send(embed=e)
                else:
                    await ctx.send("You do not have permssions to use any of the commands in that category")


            elif request[0] in [command for command in self.bot.all_commands]:
                #It is a command
                search_in = self.bot.all_commands.values()
                full_command = ""
                last_command = None
                is_group = True
                for command in request:
                    search_in = {i.name:i for i in search_in}
                    #loops through the request for command groups
                    if not command in search_in:
                        break
                    checks = search_in[command].checks
                    if [check(ctx) for check in checks] != [True for check in checks]:
                        break
                    last_command = search_in[command]
                    full_command += command+" "
                    try:
                        search_in = search_in[command].commands
                    except AttributeError:
                        is_group = False
                        break
                if not last_command:
                    await ctx.send("You are unable to use that command")
                    return
                if last_command.cog:
                    cog = last_command.cog.qualified_name.lower()
                else:
                    cog = "none"
                e = discord.Embed(title=f"{self.bot.user.name} help for {full_command}command", description=f"{last_command.description}\nFrom category - {cog}")
                if is_group:
                    e.title += " group"
                    value = ""
                    for command in search_in:
                        try:
                            checks = command.checks
                            if [check(ctx) for check in checks] == [True for check in checks]:
                                value += command.name
                                brief = command.brief
                                if brief:
                                    value += f" - {brief}"
                                value += "\n"
                        except commands.CommandError:
                            pass
                    e.add_field(name="commands", value=value)
                else:
                    params, output = [param for param in last_command.clean_params], ""
                    for param in params:
                        output += f"[{param}] "
                    e.set_footer(text=f"{ctx.prefix}{full_command} {output}")
                await ctx.send(embed=e)
                    

                
            else:
                await ctx.send("Command or category not found")

        else:
            e = discord.Embed(title=f"{self.bot.user.name} general help")
            e.set_footer(text=f"You can also do {ctx.prefix}help <command> or {ctx.prefix}help <Category>")
            
            
            for category in categories:
                value = ""
                for command in categories[category]:
                    checks = command.checks
                    try:
                        if [check(ctx) for check in checks] == [True for check in checks]:
                            if command.brief:
                                value += f"{command.name} - {command.brief}\n"
                            else:
                                value += f"{command.name}\n"
                    except commands.CommandError:
                        pass
                if len(value) != 0:
                    e.add_field(name=category, value=value, inline=False)
            await ctx.send(embed=e)
        


def setup(bot):
    bot.add_cog(none(bot))