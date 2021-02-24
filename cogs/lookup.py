import random

from discord.ext import commands
from googlesearch import search
from youtubesearchpython import Search

from config import wordsapi_headers


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
    async def define(self, ctx, word: str, idx: int = 1):
        """define a word?"""
        idx -= 1
        if idx < 0:
            return await ctx.send("try a positive number :p")
        async with self.bot.session.get(
            f"https://wordsapiv1.p.rapidapi.com/words/{word}", headers=wordsapi_headers
        ) as r:
            if r.status == 404:
                return await ctx.send(f"{word} was not found :(")
            result = await r.json()
        if "results" not in result:
            return await ctx.send(f"{word} was not found :(")
        try:
            syllables = " • ".join(result["syllables"]["list"])
        except KeyError:
            syllables = word
        try:
            definition = result["results"][idx]["definition"]
        except KeyError:
            definition = "no definition found :("
        except IndexError:
            return await ctx.send(f"Only {len(result['results'])} definitions available")
        try:
            example = result["results"][idx]["examples"][0]
        except KeyError:
            # no examples given
            example = ""

        await ctx.send(
            """
{0} | {4}

"{1}" 

{2}{3}""".format(
                syllables,
                definition,
                "*" + example + "*\n\n" if example else "",
                "Not what you were looking for? Try {0} 1-{1}".format(
                    ctx.prefix + ctx.invoked_with + " " + word,
                    len(result["results"]),
                )
                if len(result["results"]) > 1
                else "",
                result["results"][idx]["partOfSpeech"]
            )
        )


def setup(bot):
    bot.add_cog(Lookup(bot))
