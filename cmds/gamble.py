import discord
import random
import asyncio
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from core import Cog_Extension
from abc import ABC, abstractmethod

# ephemeral=True #私人訊息


class Game_driver(ABC):
    @abstractmethod
    def view(User) -> View:
        pass

    @abstractmethod
    def content(User) -> str:  # 回傳填充後的畫面字串
        pass


"""
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
            {}
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
"""


class User_data:
    def __init__(self, UserID):
        self.UserID = UserID  # 玩家ID
        self.coin = 10  # 玩家初始金錢
        Slot_Game_driver.__init_user_data__(self)  # 初始化拉霸使用者資料


class Rendering:
    class Package:
        """
        可以被渲染的抽象概念，座標為左、上角。
        """

        def __init__(self, x: int, y: int, content: list[list[str | None]]) -> None:
            self.x = x  # 最左座標點
            self.y = y  # 最上座標點
            self.content = content

    @staticmethod
    def rendering(Width: int, High: int, objects: list[Package]) -> str:
        """
        使用畫面大小(Width, High)創建畫面，依照順序渲染objects內容，支援None渲染。
        """

        screen = [
            [":black_large_square:" for _ in range(Width)] for _ in range(High)
        ]  # 創建空畫面，內容填充全灰色方格
        for object in reversed(objects):  # 跑過每個物件
            x_offset, y_offset = object.x, object.y  # 左上角=相較於0點的位移量
            content_array = object.content  # 取的物件的內容陣列
            for y in range(len(content_array)):  # 跑過每個列
                width = len(content_array[y])
                for x in range(width):  # 跑過每個列的每個元素，
                    if content_array[y][x]:  # 有內容
                        screen[y_offset + y][x_offset + x] = content_array[y][x]  # 修改畫面
        # 回傳渲染後的畫面
        return "\n".join(list(map(lambda line: "".join(list(map(str, line))), screen)))

    @staticmethod
    def balance_bars(coin: int) -> Package:
        digital_tuple = (
            ":zero:",
            ":one:",
            ":two:",
            ":three:",
            ":four:",
            ":five:",
            ":seven:",
            ":eight:",
            ":nine:",
        )
        digitals = [digital_tuple[int(numeric)] for numeric in str(coin)]  # 用文字表示數字
        return Rendering.Package(0, 0, [digitals])  # 打包並回傳

    @staticmethod
    def slot_wheel(Slot_wheel_status: list[int]):
        wheel_tuple = (":coin:", ":moneybag:", ":gem:", ":dollar:", ":credit_card:")
        wheel = [wheel_tuple[statu] for statu in Slot_wheel_status]  # 將倫盤狀態映射到表情符號
        return Rendering.Package(0, 0, [wheel])  # 打包並回傳


class Slot_Game_driver(Game_driver):
    @staticmethod
    def __init_user_data__(User):
        User.Slot_wheel_status = [0, 0, 0]  # 轉輪狀態
        User.Slot_bonus_level = 0

    @staticmethod
    def view(User: User_data) -> View:
        class embed(View):
            def __init__(self, User: User_data, *, timeout: float | None = 180):
                super().__init__(timeout=timeout)  # 初始化View
                self.User = User  # 儲存使用者在按鈕中

            @discord.ui.button(
                label="spend 1 coin", emoji="🕹️", style=ButtonStyle.green
            )
            async def game_trigger(
                self, interaction: discord.Interaction, butten: Button
            ):
                game_cost = 10  # 每局遊戲所需花費
                if not (self.User.coin >= game_cost):  # 餘額不夠啟動遊戲
                    await interaction.response.send_message(
                        "餘額不夠啟動遊戲", ephemeral=True
                    )  # 傳送訊息
                    return  # 中斷程式

                self.User.coin -= game_cost  # 扣款
                wheel_status = [random.randint(0, 4) for _ in range(3)]  # 生成隨機輪盤狀態
                self.User.Slot_wheel_status[:] = wheel_status  # 覆蓋現有輪盤狀態
                wheel_is_equal = (
                    wheel_status[0] == wheel_status[1] == wheel_status[2]
                )  # 輪盤狀態相等
                if wheel_is_equal:  # 中獎
                    self.User.Slot_bonus_level = 1 + wheel_status[0]  # 設定獎金等級是輪盤的順序
                else:
                    self.User.Slot_bonus_level = 0  # 設定獎金等級0

                await interaction.response.edit_message(
                    content=Slot_Game_driver.content(self.User),
                    view=Slot_Game_driver.view(self.User),
                )

        return embed(User)

    @staticmethod
    def content(User: User_data) -> str:
        Width = 11
        High = 4

        arrow = Rendering.Package(
            1,
            2,
            [
                [":arrow_right:", ":slot_machine:", ":arrow_right:"]
                + [None] * 3
                + [":arrow_left:", ":slot_machine:", ":arrow_left:"]
            ],
        )  # 指向中間的箭頭

        balance_bar = Rendering.balance_bars(User.coin)  # 取得餘額條
        balance_bar.x = (11 - len(balance_bar.content[0])) // 2  # 移動到置中
        balance_bar.y = 1  # 設定座標

        slot_wheel = Rendering.slot_wheel(User.Slot_wheel_status)  # 取得轉輪
        slot_wheel.x, slot_wheel.y = 4, 2  # 設定座標

        Machine_color = Rendering.Package(
            0, 0, [[":blue_square:" for _ in range(11)] for _ in range(4)]  # 9x4的藍色區域
        )

        layers = [
            balance_bar,  # 餘額條
            slot_wheel,  # 轉輪
            arrow,  # 向轉輪箭頭
            Machine_color,  # 底色
        ]
        return Rendering.rendering(Width, High, layers)


"""
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
    @staticmethod
    def __user_init__(user):
        pass

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

"""


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

        await ctx.send(Slot_Game_driver.content(User), view=Slot_Game_driver.view(User))

    @commands.command()
    async def Blackjack(self, ctx):  # 21點
        User = self.get_user(ctx.message.author.id)
        await ctx.send(
            User.blackjack_game_driver.content(), view=User.slot_game_driver.view
        )

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
