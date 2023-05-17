from dataclasses import dataclass
import discord
from discord.ext import commands
from core import Cog_Extension
from bs4 import BeautifulSoup
import json, requests, random


@dataclass
class Wordle_rely:
    with open("data.json", "r", encoding="utf8") as data:
        jdata = json.load(data)
    r = requests.get(
        "https://gist.githubusercontent.com/cfreshman/d97dbe7004522f7bc52ed2a6e22e2c04/raw/633058e11743065ad2822e1d2e6505682a01a9e6/wordle-nyt-words-14855.txt"
    )
    soup = BeautifulSoup(r.text, "html.parser")

    player = ""
    answer = ""
    in_game = False

    words = str(soup).split("\n")
    answer_times = 0
    alpha = [0 for i in range(26)]
    right_words = 0


class Wordle(Cog_Extension):
    def __init__(self, bot):
        self.wordle_rely = Wordle_rely()

    @commands.command(pass_context=True)
    async def play_wordle(self, ctx):
        self.wordle_rely.answer_times = 0
        self.wordle_rely.right_words = 0
        self.wordle_rely.alpha = [0 for i in range(26)]
        self.wordle_rely.player = ctx.author
        self.wordle_rely.answer = random.choice(self.wordle_rely.words)
        self.wordle_rely.in_game = True
        await ctx.send(f"Game Start!")

    @commands.command(pass_context=True)
    async def claer_your_mind(self, ctx):
        self.wordle_rely.__init__()
