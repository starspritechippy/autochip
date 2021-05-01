import asyncio
from typing import Optional

import discord


class Paginator:

    __slots__ = (
        "embeds",
        "timeout",
        "ordered",
        "controls",
        "controller",
        "pages",
        "current",
        "previous",
        "eof",
        "base",
        "names",
    )

    def __init__(self, **kwargs) -> None:
        self.embeds = kwargs.get("embeds", None)

        self.timeout = kwargs.get("timeout", 90)
        self.ordered = kwargs.get("ordered", False)

        self.controller = None
        self.pages: list[discord.Embed] = []
        self.base: Optional[discord.Message] = None

        self.current = 0
        self.previous = 0
        self.eof = 0

        self.controls = {
            "⏮": 0.0,
            "◀": -1,
            "⏹": "stop",
            "▶": +1,
            "⏭": None,
        }

    async def indexer(self, ctx, ctrl: str) -> None:
        if self.base is None:
            raise Exception("Should not be called manually")
        if ctrl == "stop":
            ctx.bot.loop.create_task(self.stop_controller(self.base))

        elif isinstance(ctrl, int):
            self.current += ctrl
            if self.current > self.eof or self.current < 0:
                self.current -= ctrl
        else:
            self.current = int(ctrl)

    async def reaction_controller(self, ctx) -> None:
        bot = ctx.bot
        author = ctx.author

        self.base = await ctx.send(embed=self.pages[0])

        if len(self.pages) == 1:
            await self.base.add_reaction("⏹")
        else:
            for reaction in self.controls:
                try:
                    await self.base.add_reaction(reaction)
                except discord.HTTPException:
                    return

        def check(r: discord.Reaction, u: discord.User) -> bool:
            if str(r) not in self.controls.keys():
                return False
            elif u.id == bot.user.id or r.message.id != self.base.id:
                return False
            elif u.id != author.id:
                return False
            return True

        while True:
            try:
                react, user = await bot.wait_for(
                    "reaction_add", check=check, timeout=self.timeout
                )
            except asyncio.TimeoutError:
                return ctx.bot.loop.create_task(self.stop_controller(self.base))

            control = self.controls.get(str(react))

            try:
                await self.base.remove_reaction(react, user)
            except discord.HTTPException:
                pass

            self.previous = self.current
            await self.indexer(ctx, control)

            if self.previous == self.current:
                continue

            try:
                await self.base.edit(embed=self.pages[self.current])
            except KeyError:
                pass

    async def stop_controller(self, message: discord.Message) -> None:
        try:
            await message.delete()
        except discord.HTTPException:
            pass

        try:
            self.controller.cancel()
        except Exception:
            pass

    async def paginate(self, ctx):
        if self.embeds:
            self.pages = [p for p in self.embeds if isinstance(p, discord.Embed)]

        if not self.pages:
            raise ValueError(
                "There must be enough data to create at least 1 page for pagination."
            )

        self.eof = float(len(self.pages) - 1)
        self.controls["⏭"] = self.eof
        self.controller = ctx.bot.loop.create_task(self.reaction_controller(ctx))
