import discord
import random
import asyncio
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from core import Cog_Extension
from abc import ABC, abstractmethod


class Game_driver(ABC):
    @staticmethod
    def Same_user_check(function):  # 相同玩家檢測裝飾器
        """
        這個裝飾器用於按鈕物件，調用裝飾器在運行前檢測使用者是否相同
        """

        async def same_user_check(
            self, interaction: discord.Interaction, butten: Button
        ):
            if self.User.UserID != interaction.user.id:  # 餘額不夠啟動遊戲
                await interaction.response.send_message(
                    "這是其他人啟動的遊戲局，你可以使用help查看啟動方法", ephemeral=True
                )  # 傳送訊息
                return  # 中斷程式
            await function(self, interaction, butten)  # 執行程式

        return same_user_check

    @staticmethod
    def Debit_procedures(function):  # 扣錢裝飾器
        """
        這個裝飾器用於按鈕物件，調用裝飾器檢測餘額，隨後扣款。
        """

        async def debit_procedures(
            self, interaction: discord.Interaction, butten: Button
        ):
            if not (self.User.coin >= self.game_cost):  # 餘額不夠啟動遊戲
                await interaction.response.send_message(
                    "餘額不夠啟動遊戲", ephemeral=True
                )  # 傳送訊息
                return  # 中斷
            self.User.coin -= self.game_cost  # 扣款
            await function(self, interaction, butten)  # 執行程式

        return debit_procedures

    @staticmethod  # TODO: 功能還未完善，部分遊戲鎖定功能不穩定。
    def Game_lock(function):  # 扣錢裝飾器
        """
        這個裝飾器用於按鈕物件，調用裝飾器檢測餘額，隨後扣款。
        """

        async def game_lock(self, interaction: discord.Interaction, butten: Button):
            if self.User.is_in_game:  # 使用者正在遊戲中
                await interaction.response.send_message(
                    "你正在其他遊戲中", ephemeral=True
                )  # 傳送訊息
                return  # 中斷
            self.User.is_in_game = True  # 上鎖
            await function(self, interaction, butten)  # 執行程式
            self.User.is_in_game = False  # 解鎖

        return game_lock

    @abstractmethod
    def view(User) -> View:
        pass

    @abstractmethod
    def content(User) -> str:  # 回傳填充後的畫面字串
        pass


class User_data:
    def __init__(self, UserID):
        self.UserID = UserID  # 玩家ID
        self.coin = 10  # 玩家初始金錢
        self.is_in_game = False
        Slot_Game_driver.__init_user_data__(self)  # 初始化拉霸的使用者資料
        Horses_Game_driver.__init_user_data__(self)  # 初始化賭馬的使用者資料
        Blackjack_Game_driver.__init_user_data__(self)  # 初始化賭馬的使用者資料


class Rendering:
    class Package:
        """
        可以被渲染的抽象概念，座標為左、上角。
        """

        def __init__(self, x: int, y: int, content: list[list[str | None]]) -> None:
            self.x = x  # 最左座標點
            self.y = y  # 最上座標點
            self.content = content  # 內容陣列

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
    def number_bars(number: int) -> Package:
        """
        傳入數字，回傳以圖組成的數字
        """
        digital_tuple = (
            ":zero:",
            ":one:",
            ":two:",
            ":three:",
            ":four:",
            ":five:",
            ":six:",
            ":seven:",
            ":eight:",
            ":nine:",
        )
        digitals = [digital_tuple[int(numeric)] for numeric in str(number)]  # 用文字表示數字
        return Rendering.Package(0, 0, [digitals])  # 打包並回傳

    @staticmethod
    def slot_wheel(Slot_wheel_status: list[int]) -> Package:
        """
        輸入轉輪的狀態，回傳轉輪
        """
        wheel_tuple = (":coin:", ":moneybag:", ":dollar:", ":gem:", ":credit_card:")
        wheel = [wheel_tuple[statu] for statu in Slot_wheel_status]  # 將倫盤狀態映射到表情符號
        return Rendering.Package(0, 0, [wheel])  # 打包並回傳

    @staticmethod
    def progress_bar(progress: int, max: int, color_str: str) -> Package:
        """
        輸入進度、最大上限、填充圖示字串，回傳進度條
        """
        if progress > max:  # 如果進度超過上限
            progress = max  # 限制為最大值
        return Rendering.Package(0, 0, [[color_str] * progress])  # 打包並回傳

    @staticmethod
    def horse_track(running_distance: int, width: int, footprint_str: str) -> Package:
        """
        傳入距離、寬度、填充圖示字串，回傳單條跑道
        """
        race_track = (
            [None] * (width - running_distance - 1)
            + [":horse_racing:"]
            + [footprint_str] * running_distance
        )  # 馬加上軌跡
        return Rendering.Package(0, 0, [race_track])  # 打包並回傳

    @staticmethod
    def horse_ranking(User: User_data) -> Package:
        """
        傳入使用者，回傳直向排列的馬匹排行榜
        """
        ranking = list(
            zip(
                User.Horses_running_distance,
                range(5),
                Horses_Game_driver.track_colors_str,
            )
        )  # [[距離,index,顏色],...,[距離,index,顏色]]
        random.shuffle(ranking)  # 打亂前後順序
        ranking.sort(key=lambda x: x[0], reverse=True)  # 按照名次排好

        for horse in ranking[:3]:  # 馬中前三名
            if horse[1] in User.Horses_buy_list:  # 這匹馬在購買清單裡面
                User.Horses_bonus += 15  # 獎金

        return Rendering.Package(0, 0, [[horse[2]] for horse in ranking])  # 打包並回傳

    @staticmethod
    def horse_track_group(User: User_data, X: int, Y: int) -> list[Package]:
        """
        傳入使用者物件、座標，回傳整組的賽馬軌道
        """
        track_Packages = []  # 用於處存渲染物件
        for running_distance, footprint_str, y_offset in zip(
            User.Horses_running_distance,  # 奔跑距離
            Horses_Game_driver.track_colors_str,  # 馬的顏色文字
            range(5),  # 馬的編號
        ):  # 處理各顏色的跑馬與軌跡
            racing_track = Rendering.horse_track(running_distance, 10, footprint_str)
            racing_track.x, racing_track.y = X, Y + y_offset  # 設定座標
            track_Packages.append(racing_track)  # 加入賽道
        return track_Packages  # 回傳跑道list

    @staticmethod
    def horse_ticket(User: User_data) -> Package:
        """
        渲染使用者的購票清單，回傳直向排列的購票圖示
        """
        tickets = [[None]] * 5  # 門票陣列
        for index in range(5):  # 跑過五個馬的編號
            if index in User.Horses_buy_list:  # 如果馬的編號在購買清單裡面
                tickets[index] = [":tickets:"]  # 覆蓋成票的圖案
        return Rendering.Package(0, 0, tickets)  # 打包並回傳


class Slot_Game_driver(Game_driver):
    @staticmethod
    def __init_user_data__(User):
        User.Slot_wheel_status = [0, 0, 0]  # 轉輪狀態
        User.Slot_bonus_level = 0  # 中獎等級0~5

    @staticmethod
    def view(User: User_data) -> View:
        class embed(View):
            def __init__(self, User: User_data, *, timeout: float | None = 180):
                super().__init__(timeout=timeout)  # 初始化View
                self.User = User  # 儲存使用者
                self.game_cost = 1  # 每局遊戲所需花費

            @discord.ui.button(
                label="spend 1 coin", emoji="🕹️", style=ButtonStyle.green
            )
            @Game_driver.Debit_procedures
            @Game_driver.Same_user_check
            async def game_trigger(
                self, interaction: discord.Interaction, butten: Button
            ):
                bonus_tuple = (0, 1, 5, 10, 20, 30)  # 不同階段的獎金

                wheel_status = [random.randint(0, 4) for _ in range(3)]  # 生成隨機輪盤狀態
                self.User.Slot_wheel_status[:] = wheel_status  # 覆蓋現有輪盤狀態
                wheel_is_equal = (
                    wheel_status[0] == wheel_status[1] == wheel_status[2]
                )  # 輪盤狀態相等
                if wheel_is_equal:  # 中獎
                    self.User.Slot_bonus_level = 1 + wheel_status[0]  # 設定獎金等級是輪盤的順序
                else:
                    self.User.Slot_bonus_level = 0  # 設定獎金等級0

                self.User.coin += bonus_tuple[self.User.Slot_bonus_level]  # 根據抽到的等級儲值

                await interaction.response.edit_message(
                    content=Slot_Game_driver.content(self.User),
                    view=Slot_Game_driver.view(self.User),
                )  # 修改訊息

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

        balance_bar = Rendering.number_bars(User.coin)  # 取得餘額條
        balance_bar.x = (11 - len(balance_bar.content[0])) // 2  # 移動到置中
        balance_bar.y = 1  # 設定座標

        slot_wheel = Rendering.slot_wheel(User.Slot_wheel_status)  # 取得轉輪
        slot_wheel.x, slot_wheel.y = 4, 2  # 設定座標

        Machine_color = Rendering.Package(
            0, 0, [[":blue_square:"] * 11] * 4  # 9x4的藍色區域
        )

        layers = [
            balance_bar,  # 餘額條
            slot_wheel,  # 轉輪
            arrow,  # 向轉輪箭頭
            Machine_color,  # 底色
        ]
        return Rendering.rendering(Width, High, layers)


class Horses_Game_driver(Game_driver):
    track_colors_str = [
        ":green_square:",
        ":blue_square:",
        ":orange_square:",
        ":red_square:",
        ":brown_square:",
    ]

    def __init_user_data__(User):
        User.Horses_bonus = 0  # 獎金
        User.Horses_buy_list = []  # 買的票
        User.Horses_progress = 0  # 賭馬遊戲進度
        User.Horses_running_distance = [0] * 5  # 5匹馬的距離

    @staticmethod
    def view(User: User_data) -> View:
        class embed(View):
            def __init__(self, User: User_data, *, timeout: float | None = 180):
                super().__init__(timeout=timeout)  # 初始化View
                self.User = User  # 儲存使用者
                self.game_cost = 10  # 每局遊戲所需花費
                User.horse_progress = 0

            @discord.ui.button(label="綠", emoji="🐴", style=ButtonStyle.gray)
            @Game_driver.Same_user_check
            @Game_driver.Debit_procedures
            async def buy_green(self, interaction: discord.Interaction, butten: Button):
                self.User.Horses_buy_list.append(0)  # 馬色的index加入購買清單
                await interaction.response.send_message("購買成功！", ephemeral=True)
                butten.disabled = True

            @discord.ui.button(label="藍", emoji="🐴", style=ButtonStyle.gray)
            @Game_driver.Same_user_check
            @Game_driver.Debit_procedures
            async def buy_blue(self, interaction: discord.Interaction, butten: Button):
                self.User.Horses_buy_list.append(1)  # 馬色的index加入購買清單
                await interaction.response.send_message("購買成功！", ephemeral=True)
                butten.disabled = True

            @discord.ui.button(label="橙", emoji="🐴", style=ButtonStyle.gray)
            @Game_driver.Same_user_check
            @Game_driver.Debit_procedures
            async def buy_orange(
                self, interaction: discord.Interaction, butten: Button
            ):
                self.User.Horses_buy_list.append(2)  # 馬色的index加入購買清單
                await interaction.response.send_message("購買成功！", ephemeral=True)
                butten.disabled = True

            @discord.ui.button(label="紅", emoji="🐴", style=ButtonStyle.gray)
            @Game_driver.Same_user_check
            @Game_driver.Debit_procedures
            async def buy_red(self, interaction: discord.Interaction, butten: Button):
                self.User.Horses_buy_list.append(3)  # 馬色的index加入購買清單
                await interaction.response.send_message("購買成功！", ephemeral=True)
                butten.disabled = True

            @discord.ui.button(label="棕", emoji="🐴", style=ButtonStyle.gray)
            @Game_driver.Same_user_check
            @Game_driver.Debit_procedures
            async def buy_brown(self, interaction: discord.Interaction, butten: Button):
                self.User.Horses_buy_list.append(4)  # 馬色的index加入購買清單
                await interaction.response.send_message("購買成功！", ephemeral=True)
                butten.disabled = True

        return embed(User)

    @staticmethod
    def content(User: User_data) -> str:
        Width = 15
        High = 7

        ticket = Rendering.horse_ticket(User)  # 取得門票圖層
        ticket.x, ticket.y = 14, 2  # 設定座標

        track_Packages = Rendering.horse_track_group(User, 4, 2)  # 各馬跑道
        progress_bar = Rendering.progress_bar(
            User.Horses_progress, 10, ":green_square:"
        )  # 進度條
        progress_bar.x = 4  # 設定座標
        stake_fence = Rendering.Package(4, 1, [[":wood:"] * 10])  # 木柵欄
        Leaderboard_color = Rendering.Package(
            0, 0, [[":white_large_square:"] * 4] * 7
        )  # 排行榜底色
        ranking = Rendering.Package(
            2,
            1,
            [
                [":first_place:"],
                [":second_place:"],
                [":third_place:"],
                [":cry:"],
                [":cry:"],
            ],
        )  # 排名圖示

        horse_ranking = (
            Rendering.horse_ranking(User)  # 顯示排行
            if User.Horses_progress == 19  # 進度到最後
            else Rendering.Package(0, 0, [[":question:"]] * 5)  # 顯示問號
        )  # 馬色排名
        horse_ranking.x, horse_ranking.y = 1, 1  # 設定座標

        layers = [
            ticket,
            progress_bar,  # 進度條
            *track_Packages,  # 跑馬與軌跡
            horse_ranking,  # 馬匹排名
            ranking,  # 排名圖示
            stake_fence,  # 木柵欄
            Leaderboard_color,  # 排行榜底色
        ]
        return Rendering.rendering(Width, High, layers)  # 回傳渲染畫面

    @staticmethod
    async def game_trigger(User: User_data, message: discord.Message, view: View):
        for progress in range(0, 10):  # 買票
            User.Horses_progress = progress  # 更新進度
            await message.edit(
                content=Horses_Game_driver.content(User),
                view=view,
            )  # 修改訊息刷新畫面
            await asyncio.sleep(0.5)  # 動畫等待

        for progress in range(10, 20):  # 跑馬
            User.Horses_progress = progress  # 更新進度
            User.Horses_running_distance = [
                distance + random.randint(0, 1)
                for distance in User.Horses_running_distance
            ]  # 隨機增加馬的移動距離
            await message.edit(
                content=Horses_Game_driver.content(User), view=None
            )  # 修改訊息刷新畫面
            await asyncio.sleep(0.5)  # 動畫等待

        if not User.Horses_buy_list:  # 沒買票
            return  # 中斷程式
        if User.Horses_bonus:  # 有中獎
            await message.reply(f"恭喜獲得{User.Horses_bonus}枚硬幣")  # 傳送獲獎訊息
            User.coin += User.Horses_bonus
        else:  # 沒中獎
            await message.reply("銘謝惠顧")  # 傳送獲獎訊息


class Blackjack_Game_driver(Game_driver):
    digital_tuple = (
        None,
        ":regional_indicator_a:",
        ":two:",
        ":three:",
        ":four:",
        ":five:",
        ":six:",
        ":seven:",
        ":eight:",
        ":nine:",
        ":regional_indicator_j:",
        ":regional_indicator_q:",
        ":regional_indicator_k:",
    )

    @staticmethod
    def __init_user_data__(User):
        User.Blackjack_cards = []  # 手牌
        User.Blackjack_progress = 0  # 遊戲進度(回合)

    @staticmethod
    def hand_cards_calculate(cards: list) -> int:
        card_A_amount = 0  # A卡的數量
        replace_cards = []  # 清理過的卡牌格式
        for card in cards:
            if card == 1:  # 這張卡是A
                card_A_amount += 1  # A卡計數增加
            if card >= 10:  # 10,11,12都當做10計算
                replace_cards.append(10)
            else:
                replace_cards.append(card)  # 加入卡牌

        card_total = sum(replace_cards)
        if card_A_amount and card_total <= 11:  # 有A牌 and 牌夠小
            card_total += 10  # 把1(A)當作11，所以要加10
        return card_total

    @staticmethod
    def view(User: User_data) -> View:
        class embed(View):
            def __init__(self, User: User_data, *, timeout: float | None = 180):
                super().__init__(timeout=timeout)  # 初始化View
                self.User = User  # 儲存使用者
                self.game_cost = 5  # 每局遊戲所需花費

            @discord.ui.button(label="加牌", emoji="👇", style=ButtonStyle.green)
            @Game_driver.Same_user_check
            async def hit_button(
                self, interaction: discord.Interaction, butten: Button
            ):
                pass

            @discord.ui.button(label="停牌", emoji="✋", style=ButtonStyle.red)
            @Game_driver.Same_user_check
            async def stand_button(
                self, interaction: discord.Interaction, butten: Button
            ):
                pass

            @discord.ui.button(label="雙倍下注", emoji="", style=ButtonStyle.grey)
            @Game_driver.Debit_procedures
            @Game_driver.Same_user_check
            async def double_down_button(
                self, interaction: discord.Interaction, butten: Button
            ):
                pass

        return embed(User)

    @staticmethod
    def content(User: User_data) -> str:
        Width = 11
        High = 4

        layers = []
        return Rendering.rendering(Width, High, layers)


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
        Slot_Game_driver.__init_user_data__(User)  # 初始化玩家資訊
        await ctx.send(Slot_Game_driver.content(User), view=Slot_Game_driver.view(User))

    @commands.command()
    async def Blackjack(self, ctx):  # 21點
        User = self.get_user(ctx.message.author.id)
        Blackjack_Game_driver.__init_user_data__(User)  # 初始化玩家資訊
        await ctx.send(
            Blackjack_Game_driver.content(User), view=Blackjack_Game_driver.view(User)
        )

    @commands.command()
    async def Horses(self, ctx):  # 賭馬
        User = self.get_user(ctx.message.author.id)
        Horses_Game_driver.__init_user_data__(User)  # 初始化玩家資訊
        view = Horses_Game_driver.view(User)
        message: discord.Message = await ctx.send(
            Horses_Game_driver.content(User), view=view
        )  # 送出賭馬的文字內容、包含按鈕的view
        await Horses_Game_driver.game_trigger(User, message, view)  # 啟動遊戲

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
