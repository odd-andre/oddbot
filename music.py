import json

import discord
from discord.ext import commands
import musicQueueHandler

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = musicQueueHandler.queueHandler()
        self.ffmpegOptions = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


    @commands.command(help='use !play [url] to play a song, only youtube and needs to be an url, it can be a playlist url tho', aliases=['p'])
    async def play(self,ctx,url):
        if ctx.author.voice is None:
            await ctx.channel.send('Not in voice channel, cannot join')
        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

        print('Current state: '+str(self.queue.getState(ctx.guild.id)))
        self.queue.addToQueue(url,ctx.guild.id)
        if self.queue.getState(ctx.guild.id) != 1:
            await self.play_song(ctx)

    @commands.command(help='tell the bot to fec off',aliases=['fecoff'])
    async def leave(self,ctx):
        self.queue.setState(0,ctx.guild.id)
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()


    @commands.command(help='look at the mess of a queue')
    async def queue(self,ctx):
        list = self.queue.printQueue(ctx.guild.id)
        if not list == 0:
            await ctx.channel.send(list)
        else:
            await ctx.channel.send('``` Queue is empty, use !play [url] to queue some songs ```')

    @commands.command(help='skip a shitty song')
    async def skip(self,ctx):
        ctx.voice_client.stop()
        await self.play_song(ctx)

    @commands.command()
    async def pause(self,ctx):
        if self.queue.getState(ctx.guild.id) == 1:
            self.queue.setState(2,ctx.guild.id)
            ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        if self.queue.getState(ctx.guild.id) == 2:
            self.queue.setState(1,ctx.guild.id)
            ctx.voice_client.resume()

    @commands.command(help='Clear the entire queue', aliases=['clr'])
    async def clear(self,ctx):
        self.queue.clearQueue(ctx.guild.id)

    @commands.command(help='Shuffle queue')
    async def shuffle(self,ctx):
        self.queue.shufflePlaylist(ctx.guild.id)

    @commands.command()
    async def loop(self,ctx):
        if self.queue.getLoop(ctx.guild.id) == 0:
            self.queue.setLoop(ctx.guild.id, 1)
        else:
            self.queue.setLoop(ctx.guild.id, 0)

    @commands.command()
    async def status(self,ctx):
        stateName = {1:'Playing',2:'Paused',0:'Not playing'}
        channel = ctx.channel
        musicState = self.queue.getState(ctx.guild.id)
        currentPlay = self.queue.getCurrentSongInfo(ctx.guild.id)
        loopStatus = self.queue.getLoop(ctx.guild.id)
        with open('guild_prefixes.json', 'r') as file:
            prefixes = json.load(file)
        currentPrefix = prefixes[str(ctx.guild.id)]

        message = "```"
        message += 'Prefix: '+currentPrefix+'\n'
        message += stateName[musicState]+'\n'
        if loopStatus == 1:
            message += 'Looping queue\n'

        if currentPlay != 0 and musicState != 0:
            message += 'Currently playing: '+currentPlay+'\n'

        message += "```"

        await channel.send(message)

    @commands.command(help='Remove song X from queue 1->')
    async def remove(self,ctx,songNr):
        test = 0

    @commands.command(help="Change bot prefix for this server. Default = !")
    async def setprefix(self,ctx,prefix):
        with open('guild_prefixes.json', 'r') as file:
            prefixes = json.load(file)
        prefixes[str(ctx.guild.id)] = str(prefix)

        with open('guild_prefixes.json', 'w') as file2:
            json.dump(prefixes, file2)

    async def check_queue(self,ctx):
        self.queue.setState(0,ctx.guild.id)
        await self.play_song(ctx)

    async def play_song(self,ctx):
        vc = ctx.voice_client

        print('Current state: '+str(self.queue.getState(ctx.guild.id)))
        url = 0
        if self.queue.getState(ctx.guild.id) == 0:
            url = self.queue.nextInQueue(ctx.guild.id)
        if not url == 0:
            source = await discord.FFmpegOpusAudio.from_probe(url, **self.ffmpegOptions)
            vc.play(source, after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))
            self.queue.setState(1,ctx.guild.id)


def setup(client):
    client.add_cog(Music(client))