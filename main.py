import json

import discord
from discord.ext import commands
import music, helper


def getPrefix(client,message):
    rPrefix = '!'
    with open('guild_prefixes.json','r') as file:
        prefixes = json.load(file)
        if str(message.guild.id) not in prefixes.keys():
            file.close()
            with open('guild_prefixes.json','w') as file2:
                prefixes[str(message.guild.id)] = '!'
                json.dump(prefixes,file2)
                return prefixes[str(message.guild.id)]
        else:
            return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=getPrefix, intents=discord.Intents.all())
cogs = [music, helper]
for i in range(len(cogs)):
    cogs[i].setup(client)

token = 'ODk3ODM1MDUwMzA4MTA0MjUy.YWbcDA.GpQoVIlWdzZsSyC2_N_umNzaKO8'


@client.event
async def on_guild_join(guild):
    with open('guild_prefixes.json','r') as file:
        prefixes = json.load(file)
    prefixes[str(guild.id)] = '!'

    with open('guild_prefixes.json','w') as file2:
        json.dump(prefixes,file2)


client.run(token)
