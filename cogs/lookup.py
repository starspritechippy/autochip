import random

from bs4 import BeautifulSoup
from discord.ext import commands
from googlesearch import search
from youtubesearchpython import Search


class Lookup(commands.Cog):
    """commands related to online searches"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def google(self, ctx, *, query: str):
        """google something and I'll give you a (relevant?) link"""
        async with ctx.channel.typing():
            res = random.choice(
                [
                    "let's try this",
                    "give this one a try",
                    "this might be a good starting point",
                    "here u go",
                    "here you go",
                    "alright this one looks good",
                    "let's see... try this one",
                    "this might help",
                    "hope this is what you were looking for",
                    "i tried :)\n",
                    "this is the only one i could find",
                    "hope this is the right one",
                ]
            )
            src = search(
                query, safe="off" if ctx.channel.is_nsfw() else "on", stop=1, pause=0
            )
            link = list(src)[0]
        await ctx.send(f"{res} {link}")

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, query: str):
        """find a youtube video"""
        async with ctx.channel.typing():
            src = Search(query, limit=1).result()
        result = src["result"][0]
        link = result["link"]  # noqa
        res = random.choice(
            [
                "let's try this one",
                "give this one a try",
                "this might be a good starting point",
                "here u go",
                "here you go",
                "alright this one looks good",
                "let's see... try this one",
                "hope this is what you were looking for",
                "i tried :)\n",
                "this is the best one i could find",
                "hope this is the right one",
            ]
        )
        await ctx.send(f"{res} {link}")

    @commands.command()
    async def define(self, ctx, word: str):
        """define a word?"""
        async with self.bot.session.get(
            f"https://www.merriam-webster.com/dictionary/{word.lower()}"
        ) as r:
            html = await r.text()

        html = BeautifulSoup(html, features="html.parser")
        # find the definition text
        with_tags = html.find_all("span", {"class": "dtText"})
        if not with_tags:
            return await ctx.send(
                "this word was not found :(\nplease be precise in spelling"
            )
        definitions = [
            BeautifulSoup(str(x), features="html.parser").get_text() for x in with_tags
        ]
        for d in definitions:
            d.replace(":", "")
        await ctx.send("\n---\n".join(definitions))


def setup(bot):
    bot.add_cog(Lookup(bot))
