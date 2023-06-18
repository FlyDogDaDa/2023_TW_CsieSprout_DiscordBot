from discord.ext import commands
from core import Cog_Extension
from collections import defaultdict


class TodoList(Cog_Extension):
    def __init__(self, bot):
        self.User_TodoList = defaultdict(list)

    @commands.command()
    async def add(self, ctx, *, item):  # add item in to list
        todo_list = self.User_TodoList[ctx.author]  # 取出使用者TodoList
        if not item:  # TodoList沒有內容
            await ctx.send("請提供要添加到待辦事項清單的內容。")  # 傳送失敗訊息
            return  # 中斷程式
        todo_list.append(item)  # 加入TodoList
        await ctx.send(f"已成功添加到待辦事項清單：{item}")  # 傳送成功訊息

    @commands.command()
    async def list(self, ctx):  # print list out
        todo_list = self.User_TodoList[ctx.author]  # 取出使用者TodoList
        if not todo_list:  # TodoList沒有內容
            await ctx.send("待辦事項清單是空的。")  # 傳送失敗訊息
            return  # 中斷程式
        todo_str = "\n".join(
            [f"{i+1}. {item}" for i, item in enumerate(todo_list)]
        )  # 以換行串接TodoList的每項內容、index
        await ctx.send(f"待辦事項清單：\n{todo_str}")  # 傳送TodoList內容

    @commands.command()  # Remove index from todolist
    async def remove(self, ctx, index: int):
        todo_list = self.User_TodoList[ctx.author]  # 取出使用者TodoList
        if index < 1 or index > len(todo_list):  # index小於0或超出TodoList內容數量
            await ctx.send("請提供有效的待辦事項索引以刪除。")  # 傳送失敗訊息
            return  # 中斷程式
        removed_item = todo_list.pop(index - 1)  # 將內容移除
        await ctx.send(f"已成功刪除待辦事項：{removed_item}")  # 傳送成功訊息

    @commands.command()
    async def sort(self, ctx):  # Sort todolist
        todo_list = self.User_TodoList[ctx.author]  # 取出使用者TodoList
        if not todo_list:  # TodoList沒有內容
            await ctx.send("待辦事項清單是空的。")  # 傳送失敗訊息
            return  # 中斷程式
        todo_list.sort()  # 排序TodoList
        sorted_list = "\n".join(
            [f"{i+1}. {item}" for i, item in enumerate(todo_list)]
        )  # 以換行串接TodoList的每項內容、index
        await ctx.send(f"按照字典序排序後的待辦事項清單：\n{sorted_list}")  # 傳送TodoList內容

    @commands.command()
    async def clear(self, ctx):  # Clear todolist
        todo_list = self.User_TodoList[ctx.author]  # 取出使用者TodoList
        todo_list.clear()  # 清空TodoList
        await ctx.send("所有待辦事項已清空。")  # 傳送成功訊息


async def setup(bot):
    await bot.add_cog(TodoList(bot))
