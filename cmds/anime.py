import discord
from discord.ext import commands
from core import Cog_Extension
from bs4 import BeautifulSoup
import json, requests, datetime

class Anime(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
    @commands.command(pass_context=True)
    async def anime_list(self, ctx, num:int = 3):
        if num > 20:
            await ctx.send("`一次最多顯示20個動漫!`")
            return
        headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.69"}
        r = requests.get('https://ani.gamer.com.tw/', headers=headers)
        count = 0
        if r.status_code == 200:
            await ctx.send(f'`資料獲取成功 HTTP狀態碼{r.status_code}`')
        
            soup = BeautifulSoup(r.text, 'html.parser')
            newanime_item = soup.select_one('.timeline-ver > .newanime-block')
            anime_items = newanime_item.select('.newanime-date-area:not(.premium-block)')
            
            for anime_item in anime_items:
                
                if count == num:
                    return
                anime_name = anime_item.select_one('.anime-name > p').text.strip()# 動畫名稱
                anime_watch_number = anime_item.select_one('.anime-watch-number > p').text.strip()# 觀看人數
                anime_episode = anime_item.select_one('.anime-episode').text.strip()# 動畫集數
                anime_href = anime_item.select_one('a.anime-card-block').get('href')# 觀看鏈結
                # contents：將 tag 的子節點以列表的方式輸出
                anime_date = anime_item.select_one('.anime-date-info').contents[-1].string.strip()
                anime_time = anime_item.select_one('.anime-hours').text.strip() # 日期與時間
                anime_img = anime_item.select_one('img.lazyload').get("data-src") #動漫圖片
                #embed
                embed = discord.Embed(title="動漫資訊",
                description=f"{anime_name}", color = 0xb943d0, timestamp= datetime.datetime.now())
                embed.set_image(url = anime_img)
                embed.add_field(name="觀看次數", value=f"{anime_watch_number}", inline=True)
                embed.add_field(name="集數", value=f"{anime_episode}", inline=True)
                embed.add_field(name="動畫鏈結", value=f"https://ani.gamer.com.tw/{anime_href}", inline=True)
                embed.add_field(name="上傳時間", value=f"{anime_date} {anime_time}", inline=True)
                embed.set_footer(text=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                await ctx.send(embed=embed)
                count += 1
        else:
            await ctx.send(f'請求失敗：{r.status_code}')

    @commands.command(pass_context=True)
    async def add_anime(self, ctx, *anime_name):
        anime_name = " ".join(anime_name)
        user_id = str(ctx.author.id)

        with open("data.json", "r" , encoding = "utf8") as setting:
            jdata = json.load(setting)

        if user_id not in jdata["Anime"]:
            jdata["Anime"][user_id] = [] #增加字典
        if anime_name in jdata["Anime"][user_id]:
            await ctx.send("此動漫已經在清單中。")
            return
        
        jdata["Anime"][user_id].append(anime_name)  
        
        with open("data.json", "w" , encoding = "utf8") as setting:
            json.dump(jdata, setting, indent = 4)

        await ctx.send("動漫名稱務必與動畫瘋上一字不差。")

    @commands.command(pass_context=True)
    async def remove_anime(self, ctx, *anime_name):
        anime_name = " ".join(anime_name)
        user_id = str(ctx.author.id)

        with open("data.json", "r" , encoding = "utf8") as setting:
            jdata = json.load(setting)

        if user_id not in jdata["Anime"]:
            await ctx.send("你尚未創建任何清單。")
            return
        if anime_name not in jdata["Anime"][user_id]:
            await ctx.send("清單查無此動漫。")
            return
        
        jdata["Anime"][user_id].remove(anime_name)
            
        with open("data.json", "w" , encoding = "utf8") as setting:
            json.dump(jdata, setting, indent = 4)
        await ctx.send("移除成功。")
        
    @commands.command(pass_context=True)
    async def show_anime(self, ctx):
        user_id = str(ctx.author.id)
        embed = discord.Embed(title="你的專屬動漫清單!",
                              description="清單內的動漫會在巴哈瘋更新時提醒你 :D", 
                              color = 0xb943d0, 
                              timestamp= datetime.datetime.now())
        with open("data.json", "r" , encoding = "utf8") as setting:
            jdata = json.load(setting)
        if user_id not in jdata["Anime"]:
            await ctx.send("你尚未創建任何清單。")
            return
        count = 1
        for anime in jdata["Anime"][user_id]:
            embed.add_field(name=f"{count}.", value=anime, inline=False)
            count += 1
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Anime(bot))