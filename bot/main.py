import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="/")
with open("D:\Vincent'sData\Documents\Desktop\2023資訊之芽_第二階段大作業\TOKEN.txt") as file:
    TOKEN = file.readline()


@bot.event
async def on_ready():
    print("【 Bot is online 】")


bot.run(TOKEN)
