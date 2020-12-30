from discord.ext import commands
from config import token
import os
import traceback

bot = commands.Bot(command_prefix="ok ")

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
