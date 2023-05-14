import discord
from discord.ext import commands
import asyncio, json, os

with open("seting.json", mode="r", encoding="utf8") as js:
    seting = json.load(js)

intents = discord.Intents.all()
# client = discord.Client(intents = intents)
bot = commands.Bot(command_prefix="/", intents=intents)


def run_bot():
    @bot.event
    async def on_ready():
        print(f"名為：「{bot.user}」的機器人已上線！")

    @bot.command()
    async def load(ctx, extension):
        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"{extension} loaded")

    @bot.command()
    async def unload(ctx, extension):
        await bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"{extension} unloaded")

    @bot.command()
    async def reload(ctx, extension):
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"{extension} reloaded")

    bot.run(seting["TOKEN"])


async def load_extension():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Cog:{filename} loading complete ")


asyncio.run(load_extension())
if __name__ == "__main__":
    run_bot()
