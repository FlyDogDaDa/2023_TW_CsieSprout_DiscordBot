import discord,asyncio
from discord.ext import commands
from core import Cog_Extension
import json,requests
from bs4 import BeautifulSoup

class Task(Cog_Extension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.bot = args[0]
        async def interval():
            
            await self.bot.wait_until_ready()
            count = 0
            while not self.bot.is_closed():
                with open("data.json", "r" , encoding = "utf8") as setting:
                    jdata = json.load(setting)
                # print(jdata)
                headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.69"}
                r = requests.get('https://ani.gamer.com.tw/', headers=headers)

                soup = BeautifulSoup(r.text, 'html.parser')
                newanime_item = soup.select_one('.timeline-ver > .newanime-block')
                anime_items = newanime_item.select('.newanime-date-area:not(.premium-block)')
                anime_href = anime_items[0].select_one('a.anime-card-block').get('href')# 觀看鏈結
                
                if anime_href != jdata["bahalink"]: #若網站有更新
                    for anime_item in anime_items:
                        # anime_item = anime_items[count]
                        
                        anime_name = anime_item.select_one('.anime-name > p').text.strip()# 動畫名稱
                        anime_watch_number = anime_item.select_one('.anime-watch-number > p').text.strip()# 觀看人數
                        anime_episode = anime_item.select_one('.anime-episode').text.strip()# 動畫集數
                        # contents：將 tag 的子節點以列表的方式輸出
                        anime_date = anime_item.select_one('.anime-date-info').contents[-1].string.strip()
                        anime_time = anime_item.select_one('.anime-hours').text.strip() # 日期與時間
                        anime_img = anime_item.select_one('img.lazyload').get("data-src") #動漫圖片

                        #embed
                        embed = discord.Embed(title="動畫瘋新番上架!",
                                              description=f"{anime_name}", 
                                              color = 0xb943d0)
                        embed.set_image(url = anime_img)
                        embed.add_field(name = "觀看次數", value = f"{anime_watch_number}", inline = True)
                        embed.add_field(name = "集數", value = f"{anime_episode}", inline = True)
                        embed.add_field(name = "動畫鏈結", value = f"https://ani.gamer.com.tw/{anime_href}", inline = True)
                        embed.add_field(name = "上傳時間", value = f"{anime_date} {anime_time}", inline = True)
                        anime_dict = jdata["Anime"]
                        
                        for key, value in anime_dict.items():
                            for user_anime_name in value:
                                if user_anime_name in anime_name:
                                    user = self.bot.get_user(int(key))
                                    print("已傳送一則訊息給", user)
                                    await user.send(embed = embed)
                                    break
                        # for user in jdata["Anime"]: #換頻道傳送
                        #     pass
                            # self.channel = self.bot.get_channel(channel)
                            # await self.channel.send(embed = embed)

                        #檢測是否需要傳送下一個動漫
                        if anime_time != anime_items[count+1].select_one('.anime-hours').text.strip():
                            count = 0
                            jdata["bahalink"] = anime_items[0].select_one('a.anime-card-block').get('href')
                            with open("data.json", "w" , encoding = "utf8") as setting:
                                json.dump(jdata, setting, indent = 4)
                            break
                        else: 
                            count += 1
                            anime_href = anime_items[count].select_one('a.anime-card-block').get('href')
                #60秒更新一次               
                await asyncio.sleep(60)

        self.bg_task = self.bot.loop.create_task(interval())

    # @commands.command()
    # async def set_channel(self, ctx, ch:int):
    #     self.channel = self.bot.get_channel(ch)
    #     await ctx.send(f"Set Channel: {self.channel.mention}")

# async def setup(bot):
#     await bot.add_cog(Task(bot))
def setup(bot):
    bot.add_cog(Task(bot))