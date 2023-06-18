import discord
from discord.ext import commands
from core import Cog_Extension
from bs4 import BeautifulSoup
import json, requests, random


class Player:
    def __init__(self, answer):
        self.answer_times = 0  # 使用者ask次數
        self.right_words = 0  # 正確的字數
        self.answer = answer  # 正確答案
        self.alpha = [0 for i in range(26)]  # 正確答案字母頻率表
        self.in_game = False  # 玩家是否在遊戲中


class Wordle(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        r = requests.get(
            "https://gist.githubusercontent.com/cfreshman/d97dbe7004522f7bc52ed2a6e22e2c04/raw/633058e11743065ad2822e1d2e6505682a01a9e6/wordle-nyt-words-14855.txt"
        )  # 發送請求5個字的英文單字表
        soup = BeautifulSoup(r.text, "html.parser")  # 解析HTML
        self.words = str(soup).split("\n")  # 將英文單字表轉為純文字並以換行分割
        self.players = {}  # 建立玩家dict，用於存取玩家資訊

    @commands.command(pass_context=True)
    async def ask(self, ctx, response):
        response = response.lower()  # 將使用者輸入轉為小寫
        player = self.players.get(ctx.author, 0)  # 取得玩家資訊
        if player == 0 or not player.in_game:  # 找不到玩家or玩家不在遊戲中
            await ctx.channel.send("The game doesn't start!")  # 傳送錯誤訊息
            return  # 中斷程式
        if len(response) != 5:  # 使用者輸入長度非5個字
            await ctx.channel.send(
                "The word must consist of five letters, please guess again."
            )  # 傳送錯誤訊息
            return  # 中斷程式
        if response not in self.words:  # 使用者輸入單字不在單字表(查無此單字)
            await ctx.channel.send(f"Not a word, please guess again.")  # 傳送錯誤訊息
            return  # 中斷程式

        for char in player.answer:  # 跑過正確答案
            if ord(char) >= ord("a") and ord(char) <= ord("z"):  # 如果是正常字母
                player.alpha[ord(char) - ord("a")] += 1  # 正確字母頻率增加1

        word = []  # 使用者某字母"狀態"，0:完全錯誤, 1:完全正確, 2:位置錯誤
        for _ in range(len(player.answer)):  # 跑過正確答案字串長度
            word.append(0)  # 添加0 (初始化作用)

        for i in range(len(player.answer)):  # 跑過正確答案字串長度 (判斷完全正確)
            if player.answer[i] == response[i]:  # 如果字母頻率相等
                word[i] = 1  # 答案對，位置對
                player.alpha[ord(player.answer[i]) - ord("a")] -= 1  # 扣除正確的字母頻率
        for i in range(len(player.answer)):  # 跑過正確答案字串長度 (判斷位置錯誤)
            if word[i] != 1:  # 該位置還未檢測
                if player.alpha[ord(response[i]) - ord("a")] > 0:  # 還有字母沒有完全正確
                    word[i] = 2  # 答案對，位置不對
                else:
                    player.alpha[i] = 0  # 答案不對，位置不對

        reply = []  # 回復字串圖示，用於儲存計算解果回復
        for i in range(len(player.answer)):  # 跑過正確答案長度
            if word[i] == 1:  # 該字完全正確
                reply.append(f":regional_indicator_{response[i]}:")  # 加入discord字母圖示
                player.right_words += 1  # 正確的字數增加1
            if word[i] == 2:  # 答案對，位置不對
                reply.append(":twisted_rightwards_arrows:")  # 加入discord雙箭頭圖示
            if word[i] == 0:  # 完全錯誤
                reply.append(":x:")  # 加入discord大"X"圖示

        await ctx.channel.send("".join(reply))  # 串接字串並傳送給使用者
        if player.right_words == 5:  # 五個字母全對
            await ctx.channel.send("You win! You guessed it all!")  # 傳送win訊息
            player.in_game = False  # 結束遊戲
            return  # 中斷程式
        for i in range(len(word)):  # 跑過字母狀態長度
            word[i] = 0  # 清空字母狀態
        player.answer_times += 1  # 使用者ask次數增加1

        if player.answer_times == 6:  # 六次未結束遊戲(未獲勝)
            await ctx.channel.send(
                f"You lose! The word is {player.answer}."
            )  # 傳送lose訊息
            player.in_game = False  # 結束遊戲
        player.right_words = 0  # 重製答對字母

    @commands.command(pass_context=True)
    async def play_wordle(self, ctx):
        player = Player(random.choice(self.words))  # 隨機抽取單字並建立玩家資料物件
        player.in_game = True  # 啟動遊戲
        self.players[ctx.author] = player  # 儲存玩家資料物件
        await ctx.send(f"Game Start!")  # 傳送遊戲開始訊息


async def setup(bot):  # cog初始化
    await bot.add_cog(Wordle(bot))  # 加入cog
