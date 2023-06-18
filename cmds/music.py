import discord
from discord.ext import commands
from core import Cog_Extension
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import os, asyncio
import datetime

"""
Need ffmpeg, yt-dlp, Microsoft edgedriver 114.0 version <- (可能取決於edge版本)
"""


class Music(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.music_queue = []  # 音樂待播佇列(等候清單)
        self.skip_people = []  # "跳過此音樂"投票清單
        self.voice = None  # BOT語音
        self.voiceChannel = None  # 語音頻道
        self.command_channel = None  # 訊息頻道
        self.find_musics_links = []  # 爬蟲音樂連結
        self.options = Options()  # 設定selenium webdriver的選項
        self.options.add_argument("headless")  # 不顯示視窗
        self.options.add_argument("disable-gpu")  # 取消GPU運算

    @commands.command()
    async def play(self, ctx, url):
        song_exist = os.path.isfile("song.mp3")  # 判斷檔案是否存在
        self.command_channel = ctx.channel  # 獲得訊息傳送頻道
        try:  # 嘗試移除檔案
            if song_exist:  # 有檔愛
                os.remove("song.mp3")  # 移除檔案
        except PermissionError:  # 檔案被占用(正在播放)
            self.music_queue.append(url)  # 將網址加入音樂待播佇列
            await ctx.send(
                "There is song playing now, your song had been add to queue."
            )  # 傳送加入成功訊息
            return  # 中斷程式

        voice = discord.utils.get(
            self.bot.voice_clients, guild=ctx.guild
        )  # 獲取BOT語音(可能無)

        if voice is None:  # 無BOT語音
            try:
                voiceChannel = ctx.author.voice.channel  # 嘗試取得"使用語音頻道"
            except:
                await ctx.send("你目前不在語音頻道內!")  # 傳送錯誤訊息
                return  # 中斷程式
            self.voiceChannel = voiceChannel  # 儲存語音頻道
            await voiceChannel.connect(timeout=600.0)  # 嘗試連入語音頻道
            voice = discord.utils.get(
                self.bot.voice_clients, guild=ctx.guild
            )  # 再次獲取BOT語音
        self.voice = voice  # 儲存語音
        self.skip_people.clear()  # 清空投票清單
        os.system(
            f"yt-dlp_x86.exe --extract-audio --audio-format mp3 --audio-quality 0 {url}"
        )  # 從網址下載音訊

        for file in os.listdir("./"):  # 跑過目前路徑的所有檔案
            if file.endswith(".mp3"):  # 如果檔案結尾是.mp3
                os.rename(file, "song.mp3")  # 將音檔重新命名(下載的音樂)
        await ctx.send(f"**Now playing:** {url}")  # 傳送"正在播放某音樂"訊息
        voice.play(
            discord.FFmpegPCMAudio(executable="ffmpeg.exe", source="song.mp3"),
            after=self.music_end,
        )  # 播放音樂，結束時呼叫`music_end`函式。

    def music_end(self, err=None):  # 音樂結束後會被觸發的函式
        try:  #
            if len(self.music_queue) > 0:  # 音樂待播佇列內容大於0
                song_exist = os.path.isfile("song.mp3")  # 檢查當前目錄音樂檔案是否存在
                if song_exist:  # 有音樂檔案
                    os.remove("song.mp3")  # 刪除檔案
                self.skip_people.clear()  # 清除投票清單
                next_song = self.music_queue.pop(0)  # 取出下一首音樂網址
                os.system(
                    f"yt-dlp_x86.exe --extract-audio --audio-format mp3 --audio-quality 0 {next_song}"
                )  # 下載音樂
                for file in os.listdir("./"):  # 跑過目前路徑的所有檔案
                    if file.endswith(".mp3"):  # 如果檔案結尾是.mp3
                        os.rename(file, "song.mp3")  # 將音檔重新命名(下載的音樂)
                asyncio.run_coroutine_threadsafe(
                    self.command_channel.send(f"**Now playing:** {next_song}"),
                    self.bot.loop,
                )  # 傳送"正在播放某音樂"訊息
                self.voice.play(
                    discord.FFmpegPCMAudio(executable="ffmpeg.exe", source="song.mp3"),
                    after=self.music_end,
                )  # 播放音樂
        except Exception as e:  # 產生錯誤
            print(e)  # 印出錯誤原因

    @commands.command()
    async def leave(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)  # 取得BOT語音
        self.music_queue.clear()  # 清除音樂待播佇列
        try:
            await voice.disconnect()  # 嘗試退出語音
        except:
            await ctx.send("The bot is not connected to a voice channel.")  # 傳送失敗訊息

    @commands.command()
    async def pause(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)  # 取得BOT語音
        try:
            if voice.is_playing():  # 如果音樂正在播放
                voice.pause()  # 暫停
            else:
                await ctx.send("Currently no audio is playing.")  # 傳送失敗訊息(沒有播放內容)
        except:
            await ctx.send("Bot is not connected to a voice channel.")  # 傳送失敗訊息(頻道未連結)

    @commands.command()
    async def resume(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)  # 取得BOT語音
        try:
            if voice.is_paused():  # 如果在音樂暫停
                voice.resume()  # 繼續撥播放
            else:
                await ctx.send("The audio is not paused.")  # 傳送失敗訊息(音樂沒有被暫停)
        except:
            await ctx.send("Bot is not connected to a voice channel.")  # 傳送失敗訊息(頻道未連結)

    @commands.command()
    async def stop(self, ctx):
        self.skip_people.clear()
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)  # 取得BOT語音
        try:
            voice.stop()  # 嘗試停下音樂
        except:
            await ctx.send("Bot is not connected to a voice channel.")  # 傳送失敗訊息(頻道未連結)

    @commands.command()
    async def queue(self, ctx):
        embed = discord.Embed(title="Music Queue", color=0xBE7AC7)  # 建立嵌入訊息
        index = 1  # 初始化音樂編號
        if len(self.music_queue) == 0:  # 如果沒有正在等待的音樂
            await ctx.send("There is no music in queue.")  # 傳送無等待訊息
            return  # 中斷程式
        for music_url in self.music_queue:  # 跑過等待中的音樂
            embed.add_field(
                name=f"{index}.", value=f"{music_url}", inline=False
            )  # 加到嵌入訊息
            index += 1  # 音樂編號 += 1
        await ctx.send(embed=embed)  # 傳送訊息

    @commands.command()
    async def vote(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)  # 取得BOT語音
        try:
            voiceChannel = ctx.author.voice.channel  # 嘗試取得"使用語音頻道"
        except:
            await ctx.send("You are not connected to the voice channel.")  # 傳送錯誤訊息
            return  # 中斷程式
        members = voiceChannel.members  # 取得語音頻道內人數
        try:
            if not voice.is_playing():  # 如果沒有音樂正在播放
                await ctx.send("Currently no audio is playing.")  # 傳送失敗訊息
                return  # 中斷程式
        except Exception as e:  # 出現error
            await ctx.send("Bot is not connected to a voice channel.")  # 傳送錯誤訊息(語音未連線)
            return  # 中斷程式

        if ctx.author.id in self.skip_people:  # 如果使用者已經投過票
            await ctx.send("You already voted to skip this music!")  # 傳送失敗訊息
            return  # 中斷程式
        self.skip_people.append(ctx.author.id)  # 將使用者加入投票清單

        people_needed = (
            (len(members) - 1) // 2 if len(members) % 2 == 0 else len(members) // 2 + 1
        )  # 計算跳過所需人數(半數)

        if len(self.skippeople) >= people_needed:  # 票數超過
            voice.stop()  # 停止播放音樂
            self.skip_people.clear()  # 清除投票清單
            await ctx.send("Music skipped!")  # 傳送成功訊息
        else:
            await ctx.send(
                f"Vote {len(self.skip_people)}/{people_needed}"
            )  # 傳送跳過所需人數進度

    @commands.command()
    async def find_music(self, ctx, *name):
        name = " ".join(name)  # 合併使用者輸入(查詢名稱)
        self.find_musics_links.clear()  # 清除爬蟲網址lsit
        driver = webdriver.Edge(
            "./msedgedriver.exe", options=self.options
        )  # 使用options啟動網頁
        driver.get(
            f"https://www.youtube.com/results?search_query={name}"
        )  # 使用查詢名稱跳轉到Youtube搜尋頁面

        videos_data = driver.find_elements(By.ID, "video-title")  # 找到標題元素
        datas = []  # 儲存影片標題與網址
        embed = discord.Embed(
            title="我找到了以下影片!", color=0xB943D0, timestamp=datetime.datetime.now()
        )  # 建立嵌入物件
        for data in videos_data:  # 跑過每個標題
            try:
                video_name = data.text  # 取出影片名稱
                video_link = data.get_attribute("href")  # 取出影片連結
                video_link = video_link.split("&")[0]  # 取出影片編號
                if video_link is None:  # 沒有網址
                    continue  # 跳過
            except:
                continue  # 失敗就跳過
            datas.append([video_name, video_link])  # 加入影片
            if len(datas) >= 4:  # 已獲得4部影片
                break  # 中斷迴圈

        index = 1  # 影片編號
        for name, link in datas:  # 跑過每個影片
            embed.add_field(
                name=f"{index} {name}", value=f"{link}", inline=False
            )  # 加到嵌入
            self.find_musics_links.append(link)  # 將網址加到爬蟲音樂連結
            index += 1  # 編號增加1
        await ctx.send(embed=embed)  # 傳送嵌入訊息

    @commands.command()
    async def choose_music(self, ctx, index):
        self.command_channel = ctx.channel  # 取得訊息頻道
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)  # 取得BOT語音
        if voice is None:
            try:
                voiceChannel = ctx.author.voice.channel  # 嘗試取得"使用語音頻道"
            except:
                await ctx.send("你目前不在語音頻道內!")  # 傳送錯誤訊息
                return  # 中斷程式
            self.voiceChannel = voiceChannel  # 儲存語音頻道
            await voiceChannel.connect(timeout=600.0)  # 嘗試連接
            voice = discord.utils.get(
                self.bot.voice_clients, guild=ctx.guild
            )  # 取得BOT語音

        self.voice = voice  # 儲存語音
        self.skip_people.clear()  # 清空投票清單
        try:
            index = int(index)  # 將使用者的index字串轉成int
        except:
            await ctx.send("請輸入數字")
            return  # 中斷程式
        if len(self.find_musics_links) == 0:  # 沒有爬蟲內容
            await ctx.send(
                "Nothing in music_list, you can use find_music to get list"
            )  # 傳送失敗訊息
            return  # 中斷程式
        try:
            link = self.find_musics_links[index - 1]  # 取得選中的網址
            await ctx.send("選擇成功!")  # 傳送成功訊息
            self.music_queue.append(link)  # 將選中音樂加入音樂待播清單
            self.music_end()  # 執行音樂結束函式(重新檢查狀態)
            self.find_musics_links.clear()  # 清空爬蟲list
        except Exception as e:  # 出現錯誤
            await ctx.send("清單裡好像沒有這個號碼 :(")  # 傳送失敗訊息
            return  # 中斷程式


async def setup(bot):
    await bot.add_cog(Music(bot))
