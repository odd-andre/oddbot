import discord
from discord.ext import commands

class Helper(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def helpme(self,ctx):
        await ctx.channel.send("```No fuck off\n !play [url] to queue songs, needs to be an url```")

def setup(client):
    client.add_cog(Helper(client))