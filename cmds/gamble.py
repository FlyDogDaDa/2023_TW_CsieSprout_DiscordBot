import discord
import random
import asyncio
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from core import Cog_Extension


class Slot_Game_driver:
    def __init__(self, user_data) -> None:
        self.turntable_list = [
            ":cherries:",
            ":apple:",
            ":star:",
            ":gem:",
            ":coin:",
            ":moneybag:",
        ]
        self.turntable_money_dict = {
            ":cherries:": 30,
            ":apple:": 20,
            ":star:": 50,
            ":coin:": 1,
            ":moneybag:": 100,
            ":gem:": 777,
        }
        self.screen_array = [
            ["【:slot_machine:你有{money}枚硬幣:slot_machine:】"],
            ["{Blue}", "{Green}", "{Green}", "{Green}", "{Blue}"],
            ["{Right_arrow}", "{turntables}", "{Left_arrow}"],
            ["{Blue}", "{Green}", "{Green}", "{Green}", "{Blue}"],
            [""],
        ]
        self.format_dict = {
            "Green": ":green_square:",
            "Blue": ":blue_square:",
            "Left_arrow": ":arrow_left:",
            "Right_arrow": ":arrow_right:",
            "turntables": ":black_large_square:" * 3,
            "money": user_data.coin,
        }
        self.view = self.init_view()
        self.user_data = user_data
        self.turntable = []

    def init_view(self):
        handle_button = Button(
            label="spend 1 coin", emoji="🕹️", style=ButtonStyle.green
        )
        handle_button.callback = self.pull_down
        view = View()
        view.add_item(handle_button)
        return view

    def content(self):
        content = "\n".join(["".join(y_line) for y_line in self.screen_array])
        return content.format(**self.format_dict)  # 槽填充

    def random(self):
        self.turntable = random.choices(self.turntable_list, k=3)
        self.format_dict["turntables"] = "".join(self.turntable)

    async def pull_down(self, interaction: discord.Interaction):
        if not self.user_data.coin:
            await interaction.response.send_message(":money_with_wings:你沒有硬幣了！")
            return
        self.random()
        self.user_data.coin -= 1  # 扣錢
        if self.turntable[0] == self.turntable[1] == self.turntable[2]:
            bonus = self.turntable_money_dict[self.turntable[0]]
            self.user_data.coin += bonus
            self.screen_array[4][0] = f":tada:抽中{self.turntable[0]}獎，獲得{bonus}硬幣:tada: "
        else:
            self.screen_array[4][0] = ""
        self.format_dict["money"] = self.user_data.coin
        await interaction.response.edit_message(content=self.content())


class Horses_Game_driver:
    def __init__(self, user_data) -> None:
        self.user_data = user_data
        self.leaderboard: list[str, int] = []
        self.view = self.init_view()
        self.screen_array = [
            ["【歡迎光臨投注站，你有{money}枚硬幣】"],
            [":tickets:"] * 7 + [":racehorse:"] * 5,
            [":palm_tree:" * 12],
            ["{Black}"] * 10 + ["{knight}", "{Green}"],
            ["{Black}"] * 10 + ["{knight}", "{Blue}"],
            ["{Black}"] * 10 + ["{knight}", "{Orange}"],
            ["{Black}"] * 10 + ["{knight}", "{Red}"],
            ["{Black}"] * 10 + ["{knight}", "{Brown}"],
            [":palm_tree:" * 12],
            [":arrow_down:花費10枚硬幣下注一匹馬吧:arrow_down:"],
        ]

        self.format_dict = {
            "Black": ":black_large_square:",
            "Green": ":green_square:",
            "Blue": ":blue_square:",
            "Orange": ":orange_square:",
            "Red": ":red_square:",
            "Brown": ":brown_square:",
            "knight": ":horse_racing:",
            "flag": ":checkered_flag:",
            "money": user_data.coin,
        }

    def init_view(self):
        buy_green_button = Button(label="綠馬", emoji="🐴")
        buy_blue_button = Button(label="藍馬", emoji="🐴")
        buy_orange_button = Button(label="橘馬", emoji="🐴")
        buy_red_button = Button(label="紅馬", emoji="🐴")
        buy_brown_button = Button(label="宗馬", emoji="🐴")
        # handle_button.callback = self.pull_down

        view = View()
        view.add_item(buy_green_button)
        view.add_item(buy_blue_button)
        view.add_item(buy_orange_button)
        view.add_item(buy_red_button)
        view.add_item(buy_brown_button)
        return view

    def content(self):
        content = "\n".join(["".join(y_line) for y_line in self.screen_array])
        return content.format(**self.format_dict)  # 槽填充

    def edit_progress_bar(self, index):
        self.screen_array[1][index] = "{flag}"

    def edit_horses(self):
        for y in range(3, 8):
            y_line = self.screen_array[y]
            for _ in range(random.randint(0, 2)):
                if y_line[0] == "{knight}":
                    break
                y_line.append(y_line[-1])
                y_line.pop(0)

    def show_leaderboard(self):
        for y in range(3, 8):
            y_line = self.screen_array[y]
            self.leaderboard.append((y_line[-1], y_line.count(y_line[-1])))
            random.shuffle(self.leaderboard)
            self.leaderboard.sort(reverse=True, key=lambda x: x[1])
        self.screen_array.append(self.leaderboard)
        self.screen_array.append([":first_place::second_place::third_place:"])

    def calculate(self, ctx):
        return


class User_data:
    def __init__(self, UserID):
        self.UserID = UserID  # 玩家ID
        self.coin = 87  # 玩家初始金錢
        self.slot_game_driver = Slot_Game_driver(self)  # 拉霸遊戲驅動
        self.horess_game_driver = Horses_Game_driver(self)  # 賭馬遊戲驅動


class Gamble(Cog_Extension):
    def __init__(self, bot):
        self.Users = {}  # 用ID索引玩家資訊

    def get_user(self, UserID: int) -> User_data:
        if UserID not in self.Users:  # 如果未儲存過玩家資訊
            self.Users[UserID] = User_data(UserID)  # 創建玩家資訊
        return self.Users[UserID]  # 回傳玩家資訊

    @commands.command()
    async def Slot(self, ctx):  # 拉霸機
        User = self.get_user(ctx.message.author.id)
        await ctx.send(User.slot_game_driver.content(), view=User.slot_game_driver.view)

    @commands.command()
    async def Blackjack(self, ctx):  # 21點
        User = self.get_user(ctx.message.author.id)
        await ctx.send("二十一點測試")

    @commands.command()
    async def Horses(self, ctx):  # 賭馬
        User = self.get_user(ctx.message.author.id)
        User.horess_game_driver.__init__(User)
        message: discord.Message = await ctx.send(
            User.horess_game_driver.content(), view=User.horess_game_driver.view
        )

        for progress in range(24):
            await asyncio.sleep(0.5)
            if not progress % 2:
                User.horess_game_driver.edit_progress_bar(progress // 2)
            if progress == 14:
                User.horess_game_driver.view.clear_items()
                User.horess_game_driver.screen_array.pop()  # 清除提示購買文字
            if progress >= 14:
                User.horess_game_driver.edit_horses()
            if progress == 23:
                User.horess_game_driver.enable_leaderboard()
                User.horess_game_driver.calculate(ctx)
            await message.edit(
                content=User.horess_game_driver.content(),
                view=User.horess_game_driver.view,
            )


async def setup(bot):
    await bot.add_cog(Gamble(bot))
