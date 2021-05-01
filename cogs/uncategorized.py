import random
from asyncio import sleep
from typing import Optional

import discord
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
        self.afk = {}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id not in self.afk:
            return
        del self.afk[payload.user_id]
        await self.bot.http.send_message(
            payload.channel_id,
            f"<@{payload.user_id}>, you are no longer marked as afk",
        )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id not in self.afk:
            return
        del self.afk[payload.user_id]
        await self.bot.http.send_message(
            payload.channel_id,
            f"<@{payload.user_id}>, you are no longer marked as afk",
        )

    @commands.Cog.listener()
    async def on_typing(self, channel, user, _):
        """disable afk when user is seen typing"""
        if user.id not in self.afk:
            return
        del self.afk[user.id]
        await channel.send(f"{user.mention}, you are no longer marked as afk")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """custom on_message for afk checks"""
        if message.author.id in self.afk and not message.content.lower().startswith(
            "ok afk"
        ):
            del self.afk[message.author.id]
            await message.channel.send("you are now no longer afk.")

        if not message.mentions:
            return
        if any(x in self.afk for x in [u.id for u in message.mentions]):
            afk_members = [user for user in message.mentions if user.id in self.afk]
            afk_msgs = []
            for user in afk_members:
                reason = self.afk[user.id]
                if not reason:
                    afk_msgs.append(f"{user} is set as afk.")
                else:
                    afk_msgs.append(f"{user} is set as afk: {reason}")
            resp_message = "\n\n".join(afk_msgs)
            await message.channel.send(
                resp_message,
                allowed_mentions=discord.AllowedMentions.none(),
                delete_after=len(afk_members) * 3,
            )

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

    @commands.command()
    async def ping(self, ctx):
        """gives you the ping"""
        msg = await ctx.send(
            "Here is your requested ping",
            file=discord.File(fp="assets/sonar_ping.mp3"),
        )
        await sleep(3)
        await msg.edit(
            content=msg.content + " ({}ms)".format(round(self.bot.latency * 1000, 1))
        )

    @commands.command()
    async def afk(self, ctx, *, reason: Optional[str]):
        """makes u go afk
        and if someone pings you theyre gonna know why"""
        self.afk[ctx.author.id] = reason
        await ctx.send("okay, I set you as AFK")

    @commands.group(invoke_without_command=True)
    async def epic(self, ctx, url: str):
        """guess an epic guard image"""
        async with ctx.typing():
            async with self.bot.session.get(
                "https://epic.chippy.wtf/?image={url}".format(url=url)
            ) as res:
                json = await res.json()

            guesses = [
                {
                    "guess": json["guess"],
                    "confidence": json["confidence"],
                    "emoji": discord.utils.get(
                        self.bot.get_guild(795267490124922880).emojis,
                        name=json["guess"].replace(" ", "_"),
                    ),
                }
            ]

            for i in json["other guesses"]:
                i.update(
                    {
                        "emoji": discord.utils.get(
                            self.bot.get_guild(795267490124922880).emojis,
                            name=i["guess"].replace(" ", "_"),
                        )
                    }
                )

            guesses.extend([i for i in json["other guesses"]])

        formatted = "\n".join(
            [
                "{emoji} **{name}** - {conf}% likely".format(
                    emoji=i["emoji"], name=i["guess"], conf=i["confidence"]
                )
                for i in guesses
            ]
        )

        return await ctx.send(
            "**Results for <{url}>:**\n\n{res}".format(url=url, res=formatted)
        )

    @epic.command()
    async def ai(self, ctx, url: str):
        """guess an epic guard image using ai"""
        async with ctx.typing():
            async with self.bot.session.get(
                "https://epic.chippy.wtf/ai?image={url}".format(url=url)
            ) as res:
                json = await res.json()

            guess = json["prediction"]
            emote = discord.utils.get(
                self.bot.get_guild(795267490124922880).emojis, name=guess
            )

        await ctx.send(f"This is a **{guess}** {emote}!")

    @epic.command()
    async def compare(self, ctx, url: str):
        """compare what ai thinks compared to image overlay"""
        async with ctx.typing():
            async with self.bot.session.get(
                "https://epic.chippy.wtf/?image={url}".format(url=url)
            ) as res:
                json = await res.json()
            async with self.bot.session.get(
                "https://epic.chippy.wtf/ai?image={url}".format(url=url)
            ) as res:
                json_ai = await res.json()

        guess, ai_guess = json["guess"], json_ai["prediction"]
        if guess == ai_guess:
            emote = discord.utils.get(
                self.bot.get_guild(795267490124922880).emojis,
                name=guess.replace(" ", "_"),
            )
            return await ctx.send(
                f"Both AI and image overlay agree that this is a {emote} **{guess}**!"
            )

        emote, emote_ai = discord.utils.get(
            self.bot.get_guild(795267490124922880).emojis,
            name=guess.replace(" ", "_"),
        ), discord.utils.get(
            self.bot.get_guild(795267490124922880).emojis,
            name=ai_guess.replace(" ", "_"),
        )
        await ctx.send(
            ":warning: while ai sees a {ai_emote} **{ai_guess}**, image overlay sees a {emote} **{guess}** ({conf}) :warning:".format(
                emote=emote,
                guess=guess,
                ai_emote=emote_ai,
                ai_guess=ai_guess,
                conf=json["confidence"],
            )
        )

    @commands.command()
    async def support(self, ctx):
        """get to the "support server\""""
        await ctx.send("discord.gg/vDyzrFw")

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.group(invoke_without_command=True, aliases=["bug", "feature", "fr"])
    async def feedback(self, ctx, *, text):
        """Send some feedback to the dev
        These could include feature requests, bug reports, or just some encouraging words :)"""
        if len(text) > 500:
            self.bot.get_command("feedback").reset_cooldown(ctx)
            return await ctx.send(
                "Please keep your feedback short (less than 500 characters)."
            )

        id = await self.bot.db.fetchval(
            """INSERT INTO feedback (author, content, channel, message) VALUES ($1, $2, $3, $4) RETURNING id;""",
            ctx.author.id,
            text,
            ctx.channel.id,
            ctx.message.id,
        )

        try:
            channel = self.bot.get_channel(
                827983722234118164
            ) or await self.bot.fetch_channel(827983722234118164)
        except discord.NotFound:
            return await ctx.send(
                "Could not send feedback due to an internal error, please let Chip know directly"
            )

        feedback_embed = discord.Embed(
            title="Feedback incoming!",
            description=text,
            color=discord.Color.blurple(),
        ).set_author(
            icon_url=str(ctx.author.avatar_url),
            name=f"{ctx.author} | Feedback ID {id}",
        )

        await channel.send(embed=feedback_embed)
        await ctx.send("Feedback received!")

    @commands.is_owner()
    @feedback.command(hidden=True)
    async def reply(self, ctx, id: int, *, text):
        """[owner only] reply to feedback"""
        feedback = await self.bot.db.fetchrow(
            """SELECT * FROM feedback WHERE id=$1;""", id
        )
        if not feedback:
            return await ctx.send("That feedback ID doesn't exist.")

        reply_embed = (
            discord.Embed(
                title="Your feedback got a response!",
                color=discord.Color.blurple(),
            )
            .add_field(name="Original feedback", value=feedback["content"])
            .add_field(name="Reply", value=text)
        )

        try:
            user = await self.bot.fetch_user(feedback["author"])
            await user.send(embed=reply_embed)
        except (discord.Forbidden, discord.NotFound):
            try:
                channel = await self.bot.fetch_channel(feedback["channel"])
                message = await channel.fetch_message(feedback["message"])
                await message.reply(embed=reply_embed, mention_author=True)
            except (discord.NotFound, discord.Forbidden):
                return await ctx.send("Could not send the reply.")

        await ctx.send("Reply has been sent!")


def setup(bot):
    bot.add_cog(Uncategorized(bot))
