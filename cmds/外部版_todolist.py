import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

# 創建一個待辦事項清單
todo_list = []

@bot.event
async def on_ready():
    print(f'Bot已成功登錄為 {bot.user.name}')

@bot.command()
async def add(ctx, *, item):
    if not item:
        await ctx.send('請提供要添加到待辦事項清單的內容。')
        return
    todo_list.append(item)
    await ctx.send(f'已成功添加到待辦事項清單：{item}')

@bot.command()
async def list(ctx):
    if not todo_list:
        await ctx.send('待辦事項清單是空的。')
        return
    todo_str = '\n'.join([f'{i+1}. {item}' for i, item in enumerate(todo_list)])
    await ctx.send(f'待辦事項清單：\n{todo_str}')

@bot.command()
async def remove(ctx, index: int):
    if index < 1 or index > len(todo_list):
        await ctx.send('請提供有效的待辦事項索引以刪除。')
        return
    removed_item = todo_list.pop(index - 1)
    await ctx.send(f'已成功刪除待辦事項：{removed_item}')
@bot.command()
async def clear(ctx):
    global todo_list
    todo_list = []
    await ctx.send('所有待辦事項已清空。')
@bot.command()
async def sort(ctx):
    global todo_list
    todo_list.sort()
    if not todo_list:
        await ctx.send('待辦事項清單是空的。')
    else:
        sorted_list = '\n'.join([f'{i+1}. {item}' for i, item in enumerate(todo_list)])
        await ctx.send(f'按照字典序排序後的待辦事項清單：\n{sorted_list}')



# 使用你的 Discord 機器人令牌進行登錄
bot.run('your id')
