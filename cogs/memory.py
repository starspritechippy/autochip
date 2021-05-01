import discord
from discord.ext import commands


class Memory(commands.Cog):
    """commands related to remembering and recalling things"""

    def __init__(self, bot):
        self.thoughts = {}
        self.bot = bot

    @commands.command(usage="<content>")
    async def remember(self, ctx, *, content: str = ""):
        """remember text content to recall later
        also see commands recall and forget

        results are cached, meaning if the bot restarts, the remembered things are gone"""
        if not content:
            return await ctx.invoke(self.bot.get_command("recall"))
        await self.bot.db.execute(
            """INSERT INTO memory ("user", content) VALUES ($1, $2)
            ON CONFLICT ("user") DO UPDATE
            SET content = $2;
            """,
            ctx.author.id,
            content,
        )
        await ctx.send("okay i will remember this for you")

    @commands.command()
    async def recall(self, ctx):
        """recall the remembered text content
        also view commands remember and forget

        results are cached, meaning if the bot restarts, the remembered things are gone"""
        rem = await self.bot.db.fetchval(
            """
            SELECT content FROM memory WHERE "user"=$1;
            """,
            ctx.author.id,
        )
        if not rem:
            return await ctx.send("i don't remember you telling me something...")
        await ctx.send(
            rem, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False)
        )

    @commands.command()
    async def forget(self, ctx):
        """forget the remembered text content
        also view commands remember and recall

        results are cached, meaning if the bot restarts, the remembered things are gone"""
        await self.bot.db.execute(
            """DELETE FROM memory WHERE "user"=$1;""", ctx.author.id
        )
        await ctx.send("alright, i forgot your content")


def setup(bot):
    bot.add_cog(Memory(bot))
