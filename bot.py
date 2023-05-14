# Import libraries
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Set bots
load_dotenv()
bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())


@bot.event
async def on_ready():
    for FileName in os.listdir("./cmds"):
        if FileName.endswith(".py"):
            bot.load_extension(f"cmds.{FileName[:-3]}")

    print(">>Bot is Online<<")


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cmds.{extension}")
    await ctx.send(f"Loaded")


@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f"cmds.{extension}")
    await ctx.send(f"Reloaded")


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cmds.{extension}")
    await ctx.send(f"Unloaded")


if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
