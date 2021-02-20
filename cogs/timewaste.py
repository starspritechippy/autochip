import random
from asyncio import sleep
from typing import Union

import discord
import numpy
from discord.ext import commands


def gauss(x) -> float:
    peak = 0.3
    e_fun = numpy.e ** (-0.5 * ((x - 30) / 1.76) ** 2)
    y = peak * e_fun
    return y + 0.05


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def custom_strftime(fmt, t):
    return t.strftime(fmt).replace('{S}', ordinal(t.day))


def natural_join(l):
    if len(l) == 1:
        return l[0]
    return ", ".join(l[0:-1]) + " and " + l[-1]


class InvalidLbType(discord.DiscordException):
    pass


class LbTypeConverter(commands.Converter):
    async def convert(self, ctx, arg: str):
        try:
            where = await commands.MemberConverter().convert(ctx, arg)
        except commands.MemberNotFound:
            where = arg.lower().strip()
            if where not in ["global", "personal"]:
                raise commands.MemberNotFound
        return where


class TimeWaste(commands.Cog):
    """commands related to the wastetime command"""

    def __init__(self, bot):
        self.wt_records = {}
        self.bot = bot

    async def record_time(self, time: int, user: int):
        isrecord = await self.bot.db.fetchval(
            '''
            SELECT $1 > (
              SELECT time 
              FROM timewastes
              WHERE "user"=$2
              ORDER BY time DESC
              LIMIT 1
            );
            ''', time, user
        )
        if isrecord is None:
            isrecord = True
        await self.bot.db.execute(
            '''
            INSERT INTO timewastes ("user", time, achieved, record)
            VALUES ($1, $2, now(), $3);
            ''', user, time, isrecord
        )
        return isrecord

    @commands.group(aliases=["wt", "tw", "timewaste"], invoke_without_command=True)
    async def wastetime(self, ctx):
        """waste time
        wasted time is decided at random
        leaderboard coming soon™"""
        msg = await ctx.send("Started wasting time... <a:loading:810551507694649366>")
        counter = 0
        out = gauss(0)
        rand = random.random()
        while out <= rand:
            rand = random.random()
            out = gauss(counter)
            counter += 1
            await sleep(1)

        record = await self.record_time(counter, ctx.author.id)

        await msg.edit(content="Done wasting time!")

        await ctx.send(
            "{0} you successfully wasted **{1} seconds**!\n{2}".format(
                ctx.author.mention,
                counter,
                "That's a new personal record :)" if record else ""
            )
        )

    @wastetime.command(usage="[global/@user/personal]")
    async def record(self, ctx, where: LbTypeConverter = "global"):
        """view the current record of a user, or overall"""
        if isinstance(where, discord.Member):
            result = await self.bot.db.fetchrow('''
            SELECT *
            FROM timewastes
            WHERE "user" = $1
            AND record IS TRUE
            ORDER BY time DESC, achieved ASC
            ''', where.id)

            if not result:
                return await ctx.send(f"{where.display_name} has not wasted any time yet.")

            time = result["time"]
            who = where.display_name
            when = custom_strftime("%B {S}, %Y at %I:%M%p", result["achieved"])
            desc = f"""**{who}**'s highest amount of wasted time is **{time} seconds**.
This time was achieved on **{when}**."""

        else:
            if where == "global":
                result = await self.bot.db.fetch('''
                SELECT *
                FROM timewastes
                WHERE record IS TRUE
                AND time = (SELECT MAX(time) FROM timewastes)
                ORDER BY time DESC, achieved ASC
                ''')

                if not result:
                    return await ctx.send("Nobody has not wasted any time yet.")

                time = result[0]["time"]
                achieved = result[0]["achieved"]
                when = custom_strftime("%B {S}, %Y at %I:%M%p", achieved)
                first_holder = result[0]["user"]
                who = self.bot.get_user(first_holder) or "an unknown user"
                holders = [x["user"] for x in result]
                whos = [str(self.bot.get_user(x)) or "unknown user(s)" for x in holders]
                whos = list(set(whos))
                whos.remove(str(who))
                whostr = "Other users who also hold this record are {}.".format(natural_join(whos)) if whos else ""
                desc = f"""The highest amount of wasted time is **{time} seconds**.
This time was achieved on **{when}** by **{who}**.
{whostr}
"""

            else:
                # personal record
                result = await self.bot.db.fetchrow('''
                SELECT *
                FROM timewastes
                WHERE "user" = $1
                AND record IS TRUE
                ORDER BY time DESC, achieved ASC
                ''', ctx.author.id)

                if not result:
                    return await ctx.send("You have not wasted any time yet.")

                time = result["time"]
                when = custom_strftime("%B {S}, %Y at %I:%M%p", result["achieved"])
                desc = f"""Your personal record of wasted time is **{time} seconds**.
You achieved this time on {when}."""

        record_embed = discord.Embed(
            title=f"{where} wastetime record" if isinstance(where, str) else f"{where.display_name}'s wastetime record",
            description=desc
        )
        record_embed.set_footer(text="times are in UTC format")
        await ctx.send(embed=record_embed)


def setup(bot):
    bot.add_cog(TimeWaste(bot))
