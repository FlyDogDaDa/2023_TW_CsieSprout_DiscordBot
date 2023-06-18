import discord
from discord.ext import commands
import os
from core import Cog_Extension


class Event(Cog_Extension):
    @commands.Cog.listener()
    async def on_member_join(self, member):
        g_channel = self.bot.get_channel(int(os.getenv("general_channel")))
        await g_channel.send(f"歡迎{member}加入!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, extension):  # 錯誤訊息處理
        await ctx.send(f"輸入指令發生錯誤，您可以使用help指令呼叫使用清單。")


async def setup(bot):
    await bot.add_cog(Event(bot))
