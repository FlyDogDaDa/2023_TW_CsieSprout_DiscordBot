import discord
from discord.ext import commands
from core.classes import Cog_Extension
import random


class Main(Cog_Extension):
    @commands.command()
    async def ping(
        self,
        ctx,
    ):
        # 取得延遲，換算成ms，只取小數點後兩位
        latency_ms = round(self.bot.latency * 1000, 2)
        await ctx.send(f"現在有{latency_ms}ms的延遲")

    @commands.command()
    async def choice(
        ctx,
        msg,
    ):
        contents = msg[1:-1].replace(" ", "").split(",")
        selected_content = random.choice(contents)
        await ctx.send(selected_content)


async def setup(bot):
    await bot.add_cog(Main(bot))
