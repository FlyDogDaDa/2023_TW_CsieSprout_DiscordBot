import discord
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from core import Cog_Extension
import random


class Slot_Game_driver:
    turntable_list = [
        ":cherries:",
        ":apple:",
        ":star:",
        ":gem:",
        ":coin:",
        ":moneybag:",
    ]
    turntable_money_dict = {
        ":cherries:": 30,
        ":apple:": 20,
        ":star:": 50,
        ":coin:": 1,
        ":moneybag:": 100,
        ":gem:": 777,
    }

    def __init__(self, user_data) -> None:
        self.screen_array = [
            ["【你有{money}個硬幣】"],
            ["{Blue}", "{Green}", "{Green}", "{Green}", "{Blue}"],
            ["{Right_arrow}", "{turntables}", "{Left_arrow}"],
            ["{Blue}", "{Green}", "{Green}", "{Green}", "{Blue}"],
            [""],
        ]
        self.graphic_dict = {
            "Green": ":green_square:",
            "Blue": ":blue_square:",
            "Left_arrow": ":arrow_left:",
            "Right_arrow": ":arrow_right:",
            "turntables": ":black_large_square:" * 3,
            "money": user_data.coin,
        }
        self.view = self.get_view()
        self.user_data = user_data
        self.turntable = []

    def get_view(self):
        handle_button = Button(
            label="spend 1 coin", emoji="🕹️", style=ButtonStyle.green
        )
        handle_button.callback = self.pull_down
        view = View()
        view.add_item(handle_button)
        return view

    def content(self):
        content = "\n".join(["".join(y_line) for y_line in self.screen_array])
        return content.format(**self.graphic_dict)  # 槽填充

    def random(self):
        self.turntable = random.choices(self.turntable_list, k=3)
        self.graphic_dict["turntables"] = "".join(self.turntable)

    async def pull_down(self, interaction: discord.Interaction):
        if not self.user_data.coin:
            await interaction.response.send_message("你沒有硬幣了！")
            return
        self.random()
        self.user_data.coin -= 1  # 扣錢
        if self.turntable[0] == self.turntable[1] == self.turntable[2]:
            bonus = self.turntable_money_dict[self.turntable[0]]
            self.user_data.coin += bonus
            self.screen_array[4][0] = f":tada:抽中{self.turntable[0]}獎，恭喜獲得{bonus}:tada: "
        else:
            self.screen_array[4][0] = ""
        self.graphic_dict["money"] = self.user_data.coin
        await interaction.response.edit_message(content=self.content())


class User_data:
    def __init__(self):
        self.coin = 87
        self.slot_game_driver = Slot_Game_driver(self)


class Gamble(Cog_Extension):
    # Initialization
    def __init__(self, bot):
        self.Users = {}

    # 賭馬
    @commands.command()
    async def Horses(self, ctx):
        await ctx.send("賭馬測試")

    # 拉霸機
    @commands.command()
    async def Slot(self, ctx):
        UserID = ctx.message.author.id
        if UserID not in self.Users:
            self.Users[UserID] = User_data()
        User: User_data = self.Users[UserID]
        await ctx.send(User.slot_game_driver.content(), view=User.slot_game_driver.view)

    # 21點
    @commands.command()
    async def Blackjack(self, ctx):
        await ctx.send("二十一點測試")


async def setup(bot):
    await bot.add_cog(Gamble(bot))
