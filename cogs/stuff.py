import random
from asyncio import sleep

import discord
from discord.ext import commands


def tiny_text(character: str):
    """replaces text with its subscript version"""
    regtext = "abcdefghijklmnopqrstuvwxyz"
    superscript = "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ"
    if character in regtext:
        return superscript[regtext.find(character)]
    else:
        return character


async def try_delete_message(message: discord.Message):
    try:
        await message.delete()
    except discord.Forbidden:
        pass


class Stuff(commands.Cog):
    """idk stuff i wanted to code"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def countdown(self, ctx, number: int = 3):
        """do a countdown from the number to zero.
        due to not wanting to make discord's api angry, let's keep the number below 10 okay"""
        if number > 10:
            return await ctx.send("what did i say >:(")
        nums = list(range(number))
        nums.reverse()
        nums = [i+1 for i in nums]
        for i in nums:
            await ctx.send(f"{i}...")
            await sleep(1)
        await ctx.send("go!!")

    @commands.command(name="SCREAM", aliases=["scream"])
    async def scream(self, ctx, *, text: str):
        """LET'S HIT THAT CAPS BUTTON!"""
        text = text.upper()
        if text[-1] == ".":
            text = text[:-1] + "!"

        if not text.endswith("!"):
            text += "!"

        await try_delete_message(ctx.message)
        await ctx.send(text)

    @commands.command()
    async def botsend(self, ctx, *, text: str):
        """become a superior lifeform :)"""
        try:
            webhooks = await ctx.channel.webhooks()
            if not webhooks:
                webhook = await ctx.channel.create_webhook(name="made by autochip")
            else:
                webhook = webhooks[0]
        except discord.Forbidden:
            return await ctx.send(
                "sorry i can't make you a bot :(\ntry convincing a human to give me webhook permissions"
            )

        await try_delete_message(ctx.message)
        await webhook.send(text, username=ctx.author.display_name, avatar_url=str(ctx.author.avatar_url))

    @commands.command()
    async def echo(self, ctx, *, text):
        """repeat what you tell me"""
        await try_delete_message(ctx.message)
        await ctx.send(text, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(usage="<choices separated by comma>")
    async def choose(self, ctx, *, choices):
        """for when you cant decide"""
        if not choices:
            return await ctx.send("well, i choose nothing?")

        nchoices = [x.strip() for x in choices.split(",")]
        if len(nchoices) == 1:
            return await ctx.send(f"tough choice huh...")

        final = random.choice(nchoices)
        await ctx.send(f"i chose **{final}** for you :)")

    @commands.command(aliases=["rps"])
    async def rockpaperscissors(self, ctx, choice: str):
        """lose a round of rock paper scissors against me :)"""
        if not choice.lower() in ["rock", "paper", "scissors"]:
            return await ctx.send(f"lol what's {choice} supposed to be")

        if random.randint(0,100) == 69:
            # guess we'll make it a draw
            bchoice = choice
            outcome = "that's a draw"
        else:
            outcome = "you lost lol"
            if choice == "rock":
                bchoice = "paper"
            elif choice == "paper":
                bchoice = "scissors"
            else:
                bchoice = "rock"

        await ctx.send(f"you chose {choice}, i chose {bchoice}. {outcome}")

    @commands.command()
    async def whisper(self, ctx, *, text):
        """turn text into subscript making it freaking tiny"""
        textmap = map(tiny_text, list(text.lower()))
        whisper_text = ("".join(list(textmap))).rstrip(".?!")
        whisper_text += "..."
        await try_delete_message(ctx.message)
        await ctx.send(whisper_text)


def setup(bot):
    bot.add_cog(Stuff(bot))
