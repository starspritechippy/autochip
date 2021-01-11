import os
import re
import traceback

import aiohttp
import discord
from discord.ext import commands

from config import prefix, token

fallback = os.urandom(32).hex()


def get_pre(_, msg):
    comp = re.compile("^(" + "|".join(map(re.escape, prefix)) + ").*", flags=re.I)
    match = comp.match(msg.content)
    if match is not None:
        return match.group(1)
    return fallback


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=get_pre, intents=intents)
bot.session = aiohttp.ClientSession()

for cog in os.listdir("cogs"):
    if cog.endswith(".py"):
        try:
            bot.load_extension(f"cogs.{cog[:-3]}")
            print(f"{cog[:-3]} loaded successfully")
        except commands.ExtensionError:
            traceback.print_exc()
bot.load_extension("jishaku")


@bot.event
async def on_ready():
    print("Autochip ready to rock")


bot.run(token)
