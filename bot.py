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
            try:
                await bot.load_extension(f"cmds.{FileName[:-3]}")
                print(f"載入成功！Cog:{FileName}")
            except Exception as ex:
                print(f"△載入失敗Cog:{FileName}")
                print(ex)

    print(">>Bot is Online<<")


@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f"cmds.{extension}")
    await ctx.send(f"Loaded")


@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f"cmds.{extension}")
    await ctx.send(f"Reloaded")


@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f"cmds.{extension}")
    await ctx.send(f"Unloaded")


@bot.event
async def on_command_error(ctx, extension):
    await ctx.send(f"輸入指令發生錯誤，您可以使用help指令呼叫使用清單。")


if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
