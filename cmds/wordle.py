import discord
from discord.ext import commands
import json
from core import Cog_Extension
import urllib
import random


class Wordle(Cog_Extension):
    # Initialization
    def __init__(self, bot):
        pass

        """
        TODO 
        要在init function 中載入單字庫

        Hint:
        1. 好像有import urllib
        2. data.json中有貼上url了
        """

    @commands.command()
    async def Play(self, ctx):
        pass

        """
        TODO 
        要在爬好的單字庫中, 隨機挑選一個單字做為預設的答案
        """

    @commands.command()
    async def Ask(self, ctx, ans):
        pass

        """
        ans 是使用者傳入的猜測答案

        TODO
        1. 沒有play直接ask : 請先輸入 Play 指令
        2. 不是5個字的單字 : 請輸入5個字母的單字
        3. 不是單字的英文組合(不在單字庫中) : 這好像不是個單字
        4. 答對 : 恭喜答對!!!
        5. 猜太多次了 : 真可惜, 答案是{answer}
        """


async def setup(bot):
    await bot.add_cog(Wordle(bot))
