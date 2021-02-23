import random
from asyncio import sleep

import discord
import numpy
from discord.ext import commands

from utils.image import get_bytes, image_to_ascii


async def try_delete_message(message: discord.Message):
    try:
        await message.delete()
    except discord.Forbidden:
        pass


class Uncategorized(commands.Cog):
    """commands that don't fit into other categories"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ascii", usage="<emoji or attached image>")
    async def make_ascii(self, ctx, emoji: discord.PartialEmoji = None):
        """turn an emoji or image into ascii art
        emoji have priority"""
        if not emoji:
            if not ctx.message.attachments:
                return await ctx.send("```\n```")
            url = str(ctx.message.attachments[0].url)
        else:
            url = str(emoji.url)
        ascii_art = image_to_ascii(await get_bytes(self.bot, url))
        await ctx.send(f"```{ascii_art}```")

    @commands.command(aliases=["temp", "temparature"])
    async def temperature(self, ctx, temp: str):
        """translate between celsius and fahrenheit
        expected inut is, for example would be 35c"""
        try:
            if temp[-1].lower() == "f":
                new_temp, unit = ((int(temp[:-1].strip()) - 32) * (5 / 9), "C")
            elif temp[-1].lower() == "c":
                new_temp, unit = ((int(temp[:-1].strip()) * (9 / 5)) + 32, "F")
            else:
                return await ctx.send(
                    "invalid temperature given, did you forget the c or f at the end?"
                )
        except ValueError:
            return await ctx.send(
                "invalid temperature format, try <number>[c/f], for example 35c"
            )

        await ctx.send(f"that's **{new_temp:,.1f}°{unit}**")

    @commands.command(aliases=["rc", "randomcolour"])
    async def randomcolor(self, ctx):
        """show you a random color :)"""
        col = random.randint(0, 16777215)
        recol = str(hex(col).split("x")[1])
        r, g, b = recol[0:2], recol[2:4], recol[4:6]
        embed = discord.Embed(
            title="#" + recol.upper(),
            url=f"https://www.color-hex.com/color/{recol}",
            description=f"""Red: {int(r, base=16)}
Green: {int(g, base=16)}
Blue: {int(b, base=16)}""",
            color=col,
        )
        embed.set_image(url=f"https://htmlcolors.com/color-image/{recol}.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def submit(self, ctx, *, content: str = None):
        """submits an event submission anonymously to the event submission channel
        attached files will be sent as well"""
        attachments = ctx.message.attachments
        files = [await attachment.to_file() for attachment in attachments]
        await try_delete_message(ctx.message)
        guild = self.bot.get_guild(738627945056174230)
        channel = guild.get_channel(760366600284799016)
        try:
            await channel.send(content, files=files)
        except discord.HTTPException:
            # someone tried to send an empty message
            await ctx.send("You can't submit nothing :(", delete_after=5)

    @commands.command()
    async def invite(self, ctx):
        """get an invite link so I can join your server"""
        await ctx.send(
            "<https://discord.com/api/oauth2/authorize?client_id=793856553631350804&permissions=387072&scope=bot>"
        )

    @commands.command(aliases=["gn"])
    async def goodnight(self, ctx):
        """gn"""
        await sleep(0.5)
        cy = random.choice(
            [
                "gn hun",
                "gn hon",
                "good night cute",
                "good night bb",
                "goodnight :*",
                "night night",
                "good night luv",
            ]
        )
        await ctx.send(cy)
        if not ctx.guild:
            return
        await sleep(0.5)
        await ctx.send(f"??cuddle {ctx.author.mention}")


def setup(bot):
    bot.add_cog(Uncategorized(bot))
