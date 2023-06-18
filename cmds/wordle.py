import discord
from discord.ext import commands
from core import Cog_Extension
from bs4 import BeautifulSoup
import json, requests, random


class Player:
    def __init__(self, answer):
        self.answer_times = 0
        self.right_words = 0
        # self.player = ""
        self.answer = answer
        # self.in_game = False
        self.alpha = [0 for i in range(26)]
        self.in_game = False


class Wordle(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        with open("data.json", "r", encoding="utf8") as data:
            jdata = json.load(data)
        r = requests.get(
            "https://gist.githubusercontent.com/cfreshman/d97dbe7004522f7bc52ed2a6e22e2c04/raw/633058e11743065ad2822e1d2e6505682a01a9e6/wordle-nyt-words-14855.txt"
        )
        soup = BeautifulSoup(r.text, "html.parser")

        self.players = {}
        # self.player = ""
        # self.answer = ""
        # self.in_game = False

        self.words = str(soup).split("\n")
        # self.answer_times = 0
        # self.alpha = [0 for i in range(26)]
        # self.right_words = 0

    @commands.command(pass_context=True)
    async def ask(self, ctx, response):
        response = response.lower()
        # print(response)
        # global alpha, answer_times, right_words, player, answer, in_game
        player = self.players.get(ctx.author, 0)
        if player == 0 or not player.in_game:
            await ctx.channel.send("The game doesn't start!")
            return
        # if ctx.author != self.player:
        #     await ctx.channel.send("You aren't player!")
        #     return
        if len(response) != 5:
            await ctx.channel.send(
                "The word must consist of five letters, please guess again."
            )
            return
        if response not in self.words:
            await ctx.channel.send(f"Not a word, please guess again.")
            return

        for char in player.answer:
            if ord(char) >= ord("a") and ord(char) <= ord("z"):
                player.alpha[ord(char) - ord("a")] += 1

        word = []
        for _ in range(len(player.answer)):
            word.append(0)
        for i in range(len(player.answer)):
            if player.answer[i] == response[i]:
                word[i] = 1  # 答案對，位置對
                player.alpha[ord(player.answer[i]) - ord("a")] -= 1
        for i in range(len(player.answer)):
            if word[i] != 1:
                if player.alpha[ord(response[i]) - ord("a")] > 0:
                    word[i] = 2  # 答案對，位置不對
                else:
                    player.alpha[i] = 0  # 答案不對，位置不對
        reply = []
        for i in range(len(player.answer)):
            if word[i] == 1:
                reply.append(f":regional_indicator_{response[i]}:")
                player.right_words += 1
            if word[i] == 2:
                reply.append(":twisted_rightwards_arrows:")
            if word[i] == 0:
                reply.append(":x:")
        await ctx.channel.send("".join(reply))
        if player.right_words == 5:
            await ctx.channel.send("You win! You guessed it all!")  # 五個字母全對
            player.in_game = False
            return
        for i in range(len(word)):
            word[i] = 0
        player.answer_times += 1

        if player.answer_times == 6:  # 六次未全對
            await ctx.channel.send(f"You lose! The word is {player.answer}.")
            player.in_game = False
        player.right_words = 0

    @commands.command(pass_context=True)
    async def play_wordle(self, ctx):
        # global alpha, answer_times, right_words, player, answer, in_game
        player = Player(random.choice(self.words))
        player.in_game = True
        # print(player.answer)
        self.players[ctx.author] = player
        # self.answer_times = 0
        # self.right_words = 0
        # self.alpha = [0 for i in range(26)]
        # self.player = ctx.author
        # self.answer = random.choice(self.words)
        # self.in_game = True
        await ctx.send(f"Game Start!")


async def setup(bot):
    await bot.add_cog(Wordle(bot))
