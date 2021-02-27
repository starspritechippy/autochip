import math

import discord
from discord.ext import commands, menus


class CogMenu(menus.Menu):
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop("title")
        self.description = kwargs.pop("description")
        self.bot = kwargs.pop("bot")
        self.color = discord.Color.blurple()
        self.footer = kwargs.pop("footer")
        self.per_page = kwargs.pop("per_page", 5)
        self.page = 1
        super().__init__(*args, timeout=60.0, delete_message_after=True, **kwargs)

    @property
    def pages(self):
        return math.ceil(len(self.description) / self.per_page)

    def embed(self, desc):
        e = discord.Embed(
            title=self.title, color=self.color, description="\n".join(desc)
        )
        e.set_footer(
            text=f"{self.footer} | Page {self.page}/{self.pages}",
            icon_url=self.bot.user.avatar_url_as(static_format="png"),
        )
        return e

    def should_add_reactions(self):
        return len(self.description) > self.per_page

    async def send_initial_message(self, ctx, channel):
        e = self.embed(self.description[0 : self.per_page])
        return await channel.send(embed=e)

    @menus.button("\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f")
    async def page_back(self, _):
        if self.page != 1:
            self.page -= 1
            start = (self.page - 1) * self.per_page
            end = self.page * self.per_page
            items = self.description[start:end]
            e = self.embed(items)
            await self.message.edit(embed=e)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def stop_menu(self, _):
        self.stop()

    @menus.button("\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f")
    async def page_forward(self, _):
        if len(self.description) >= (self.page * self.per_page):
            self.page += 1
            start = (self.page - 1) * self.per_page
            end = self.page * self.per_page
            items = self.description[start:end]
            e = self.embed(items)
            await self.message.edit(embed=e)


class SubcommandMenu(menus.Menu):
    def __init__(self, *args, **kwargs):
        self.cmds = kwargs.pop("cmds")
        self.title = kwargs.pop("title")
        self.description = kwargs.pop("description")
        self.bot = kwargs.pop("bot")
        self.color = discord.Color.blurple()
        self.per_page = kwargs.pop("per_page", 5)
        self.page = 1
        super().__init__(*args, timeout=60.0, delete_message_after=True, **kwargs)

    @property
    def pages(self):
        return math.ceil(len(self.cmds) / self.per_page)

    def embed(self, cmds):
        e = discord.Embed(
            title=self.title, color=self.color, description=self.description
        )
        e.add_field(
            name="subcommands",
            value="\n".join(
                [
                    f"`{'+' if isinstance(c, commands.Group) else '•'}"
                    f" {self.ctx.prefix}{c.qualified_name}` - {c.brief or c.short_doc}"
                    for c in cmds
                ]
            ),
        )
        if self.should_add_reactions():
            e.set_footer(
                icon_url=self.bot.user.avatar_url_as(static_format="png"),
                text="click on the reactions to see more subcommands. | Page"
                " {start}/{end}".format(start=self.page, end=self.pages),
            )
        return e

    def should_add_reactions(self):
        return len(self.cmds) > self.per_page

    async def send_initial_message(self, ctx, channel):
        e = self.embed(self.cmds[0 : self.per_page])
        return await channel.send(embed=e)

    @menus.button("\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f")
    async def page_back(self, _):
        if self.page != 1:
            self.page -= 1
            start = (self.page - 1) * self.per_page
            end = self.page * self.per_page
            items = self.cmds[start:end]
            e = self.embed(items)
            await self.message.edit(embed=e)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def stop_menu(self, _):
        self.stop()

    @menus.button("\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f")
    async def page_forward(self, _):
        if len(self.cmds) >= (self.page * self.per_page):
            self.page += 1
            start = (self.page - 1) * self.per_page
            end = self.page * self.per_page
            items = self.cmds[start:end]
            e = self.embed(items)
            await self.message.edit(embed=e)


class HelpCommand(commands.HelpCommand):
    """custom help command"""

    # overwrite send_bot_help(command_mapping[cog, command])
    # send the standard bot help with all commands and all cogs
    async def send_bot_help(self, mapping):
        return await self.context.send("there is no help")

    # overwrite send_cog_help(cog)
    # send the help for a cog, commands can be accessed with cog.commands
    async def send_cog_help(self, cog):
        menu = CogMenu(
            title=(
                f"{len(set(cog.walk_commands()))} commands in the {cog.qualified_name} cog"
            ),
            bot=self.context.bot,
            description=[
                f"`{'+' if isinstance(c, commands.Group) else '•'}"
                f" {self.clean_prefix}{c.qualified_name} {c.usage or c.signature}` - {c.brief or c.short_doc}"
                for c in cog.get_commands()
            ],
            footer="See '{prefix}help <command>' for more detailed info".format(
                prefix=self.clean_prefix
            ),
        )

        await menu.start(self.context)

    async def send_group_help(self, group):
        menu = SubcommandMenu(
            title=(
                f"{group.qualified_name} commands (from the {group.cog.qualified_name} cog)"
            ),
            bot=self.context.bot,
            description=f"""{group.usage or group.signature}

{group.help}""",
            cmds=list(group.commands),
        )
        await menu.start(self.context)

    async def send_command_help(self, command):
        e = discord.Embed(
            title=(
                f"{command.qualified_name} (from the {command.cog.qualified_name} cog)"
            ),
            color=discord.Color.blurple(),
            description=f"""{command.usage or command.signature}

{command.help}""",
        )

        if command.aliases:
            e.add_field(name="aliases", value="{}".format(" • ".join(command.aliases)))
        await self.context.send(embed=e)

    # overwrite command_callback(self, ctx, *, input)
    # checks to see whether any given input is a cog, group, command, or invalid


class Help(commands.Cog):
    """h"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = HelpCommand()


def setup(bot):
    bot.add_cog(Help(bot))
