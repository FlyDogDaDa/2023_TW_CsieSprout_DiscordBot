import discord
from discord.ext import commands
import json
from core import Cog_Extension


class Main(Cog_Extension):
    @commands.command()
    async def Hello(self, ctx):
        await ctx.send("Hello, world")


async def setup(bot):
    await bot.add_cog(Main(bot))
