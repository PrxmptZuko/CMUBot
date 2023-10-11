import discord
from discord.ext import commands

async def random_image(ctx):
    print("Pulling a random image")
    with open('meme_images/sait.jpg', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)