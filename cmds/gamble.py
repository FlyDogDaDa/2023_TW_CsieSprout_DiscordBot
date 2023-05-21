from typing import Optional
import discord
import random
import asyncio
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from cmds.gamble import Game_driver
from core import Cog_Extension


class Game_driver:
    screen_array = []
    format_dict = {}
    game_spend = 0
    deduction_failure_message = ":money_with_wings:你沒有足夠的硬幣！"
    deduction_success_message = "扣款成功！"

    def content(self) -> str:  # 回傳填充後的畫面字串
        content = "\n".join(["".join(y_line) for y_line in self.screen_array])
        return content.format(**self.format_dict)  # 槽填充
        # await interaction.response.send_message(":money_with_wings:你沒有足夠的硬幣！")

    @staticmethod
    def Payment_process(user, amount: int) -> bool:
        if user.coin >= amount:  # 硬幣足夠
            user.coin -= amount  # 扣款
            return True  # 回傳付款成功
        return False  # 回傳付款失敗


class Game_View(View):
    def __init__(
        self,
        *,
        game_driver: Game_driver,
        trigger_function=lambda x: x,
        definition_buttons_list: list[dict] = [{}],
        timeout: float | None = 180,
    ):
        self.game_driver = game_driver  # 指向遊戲驅動
        for button_dict in definition_buttons_list:

            @discord.ui.button(**button_dict)
            async def button_function(interaction, button):
                await self.Payment_process(interaction, button)

            self[button_dict[""]] = button_function

    def trigger_function():
        pass

    async def Payment_process(
        self, interaction: discord.Interaction, button: Button
    ) -> bool:
        if not self.game_driver.Payment_process(
            self.game_driver.user_data, self.game_driver.game_spend
        ):
            # 發送失敗訊息
            await interaction.response.send_message(
                self.game_driver.deduction_failure_message
            )
            return  # 使用回傳跳出
        # 執行應被觸發的程式
        self.trigger_function(button)
        # 發送成功訊息
        await interaction.response.send_message(
            self.game_driver.deduction_success_message
        )


class Slot_Game_View(Game_View):
    def __init__(
        self,
        *,
        game_driver: Game_driver,
    ):
        buttons_list = [
            {"label": "spend 1 coin", "emoji": "🕹️", "style": ButtonStyle.green}
        ]
        super().__init__(
            game_driver=game_driver,
            definition_buttons_list=buttons_list,
            trigger_function=self.trigger_function,
        )

    def trigger_function(self, button):
        self.game_driver.random()
        turntable = self.game_driver.turntable
        if turntable[0] == turntable[1] == turntable[2]:
            bonus = self.game_driver.turntable_money_dict[turntable[0]]
            self.game_driver.user_data.coin += bonus
            self.game_driver.screen_array[4][
                0
            ] = f":tada:抽中{self.turntable[0]}獎，獲得{bonus}硬幣:tada: "
        else:
            self.game_driver.screen_array[4][0] = ""
        self.game_driver.format_dict["money"] = self.user_data.coin


class Horses_Game_View(Game_View):
    def __init__(self, *, game_driver: Game_driver):
        buttons_list = [
            {"label": "Green", "emoji": "🐴"},
            {"label": "Blue", "emoji": "🐴"},
            {"label": "Orange", "emoji": "🐴"},
            {"label": "Red", "emoji": "🐴"},
            {"label": "Brown", "emoji": "🐴"},
        ]
        self.game_driver = game_driver  # 指向遊戲驅動
        super().__init__(
            game_driver=game_driver,
            definition_buttons_list=buttons_list,
        )

    def trigger_function(self, button):
        self.game_driver.bet.append("{" + button.label + "}")


class Slot_Game_driver(Game_driver):
    def __init__(self, user_data) -> None:
        self.view = self.init_view()
        self.user_data = user_data
        self.turntable = []
        self.game_spend = 1
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

    def random(self):
        self.turntable = random.choices(self.turntable_list, k=3)
        self.format_dict["turntables"] = "".join(self.turntable)


class Horses_Game_driver(Game_driver):
    def __init__(self, user_data) -> None:
        self.view = Horses_Game_View(game_driver=self)
        self.user_data = user_data
        self.leaderboard_str: str = []
        self.leaderboard: list[list[int, int, str]] = []
        self.bet = []
        self.game_spend = 10
        self.screen_array = [
            ["【歡迎光臨投注站】"],
            [":tickets:"] * 7 + [":racehorse:"] * 5,
            [":palm_tree:" * 12],
            ["{Black}"] * 10 + ["{knight}", "{Green}"],
            ["{Black}"] * 10 + ["{knight}", "{Blue}"],
            ["{Black}"] * 10 + ["{knight}", "{Orange}"],
            ["{Black}"] * 10 + ["{knight}", "{Red}"],
            ["{Black}"] * 10 + ["{knight}", "{Brown}"],
            [":palm_tree:" * 12],
            [":arrow_down:花費10枚硬幣下注可能會進入前三名的馬匹吧:arrow_down:"],
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

    def content(self) -> str:
        content = "\n".join(["".join(y_line) for y_line in self.screen_array])
        return content.format(**self.format_dict)  # 槽填充

    def edit_progress_bar(self, index) -> None:
        self.screen_array[1][index] = "{flag}"

    def edit_horses(self, timestamp: int) -> None:
        for y in range(3, 8):
            y_line = self.screen_array[y]
            color = y_line[-1]

            for _ in range(random.randint(0, 2)):
                if y_line[0] == "{knight}":  # 抵達終點
                    if not list(
                        filter(lambda x: x[2] == color, self.leaderboard)
                    ):  # 沒加入過計分板
                        self.leaderboard.append([timestamp, 11, color])  # 加入記分板
                    break
                y_line.append(color)
                y_line.pop(0)

    def show_leaderboard(self) -> None:
        for y in range(3, 8):
            y_line = self.screen_array[y]
            color = y_line[-1]
            if not list(filter(lambda x: x[2] == color, self.leaderboard)):
                self.leaderboard.append([24, y_line.count(color), color])  # 加入記分板

        random.shuffle(self.leaderboard)
        self.leaderboard.sort(reverse=True, key=lambda x: x[1])  # 先排距離
        self.leaderboard.sort(key=lambda x: x[0])  # 再排時間
        self.leaderboard_str = [horse[2] for horse in self.leaderboard]
        self.screen_array.append(self.leaderboard_str)
        self.screen_array.append([":first_place::second_place::third_place:"])

    def calculate(self) -> str:
        bonus = 0
        for color in self.bet:
            if color in self.leaderboard_str[:3]:
                bonus += 15
        self.user_data.coin += bonus
        if bonus:
            return f"眼光真好，恭喜你選擇的馬匹為你贏得{bonus}枚硬幣"
        return f"很可惜這次沒有買中寶馬，下次運氣會更好！"


class Blackjack_Game_driver(Game_driver):
    def __init__(self, user_data) -> None:
        self.user_data = user_data
        self.view = self.init_view()
        self.game_spend = 5
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

    def init_view(self):
        hit_button = Button(label="加牌", emoji="👇", style=ButtonStyle.green)
        stand_button = Button(label="停牌", emoji="✋", style=ButtonStyle.red)
        double_down_button = Button(label="雙倍下注", emoji="💰👆", style=ButtonStyle.grey)
        hit_button.callback = self.hit
        stand_button.callback = self.stand
        double_down_button.callback = self.double_down
        view = (
            View()
            .add_item(hit_button)
            .add_item(stand_button)
            .add_item(double_down_button)
        )
        return view

    async def Payment_process(self, interaction: discord.Interaction) -> bool:
        pass

    async def hit(self, interaction: discord.Interaction):
        pass

    async def stand(self, interaction: discord.Interaction):
        pass

    async def double_down(self, interaction: discord.Interaction):
        pass


class User_data:
    def __init__(self, UserID):
        self.UserID = UserID  # 玩家ID
        self.coin = 10  # 玩家初始金錢
        self.slot_game_driver = Slot_Game_driver(self)  # 拉霸遊戲驅動
        self.horess_game_driver = Horses_Game_driver(self)  # 賭馬遊戲驅動
        self.blackjack_game_driver = Blackjack_Game_driver(self)  # 21點遊戲驅動


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
        User.horess_game_driver.__init__(User)  # 初始化驅動器(清除前次內容)
        message: discord.Message = await ctx.send(
            User.horess_game_driver.content(), view=User.horess_game_driver.view
        )  # 送出賭馬的文字內容、包含按鈕的view

        for progress in range(24):  # 12
            await asyncio.sleep(0.5)  # 為了動畫等待半秒
            if not progress % 2:  # 如果是整數(一秒)
                User.horess_game_driver.edit_progress_bar(progress // 2)  # 更新進度條
            if progress == 14:  # 進入賽馬階段
                User.horess_game_driver.view.clear_items()  # 清除購買按鈕
                User.horess_game_driver.screen_array.pop()  # 清除提示購買文字
            if progress >= 14:  # 賽馬階段中
                User.horess_game_driver.edit_horses(progress)  # 修改馬的位置
            if progress == 23:  # 結束
                User.horess_game_driver.show_leaderboard()  # 顯示記分板
                calculate_text = User.horess_game_driver.calculate()  # 結算金額
                await ctx.send(calculate_text)  # 回傳計算後結果
            await message.edit(
                content=User.horess_game_driver.content(),
                view=User.horess_game_driver.view,
            )  # 修改訊息刷新畫面

    @commands.command()
    async def Wash_dishes(self, ctx):  # 洗碗
        User = self.get_user(ctx.message.author.id)
        User.coin += 5
        await ctx.send("你幫別人洗碗，獲得5枚硬幣")

    @commands.command()
    async def wallet(self, ctx):  # 查看餘額
        User = self.get_user(ctx.message.author.id)  # 找到使用者
        await ctx.send(f"你擁有{User.coin}枚硬幣")  # 發送玩家擁有的硬幣


async def setup(bot):
    await bot.add_cog(Gamble(bot))


async def setup(bot):
    await bot.add_cog(Gamble(bot))
