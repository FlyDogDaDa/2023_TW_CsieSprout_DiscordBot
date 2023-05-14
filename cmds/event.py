import discord
from discord.ext import commands
import os
from core import Cog_Extension

class Event(Cog_Extension):

    @commands.Cog.listener()
    async def on_member_join(self, member):
        g_channel = self.bot.get_channel(int(os.getenv("general_channel")))
        await g_channel.send(f"歡迎{member}加入!")

    '''
    TODO (optional)
    Add other events such as on_message, on_command_error
    '''
    
async def setup(bot):
    await bot.add_cog(Event(bot))