from multiprocessing.connection import Client
import discord
from discord.ext import commands
from discord.flags import Intents
from discord.player import FFmpegPCMAudio
import youtube_dl
from youtube_dl.YoutubeDL import YoutubeDL

intents = Intents.default();
client = commands.Bot(command_prefix='*')

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.find('@입장') > -1:
        await message.author.voice.channel.connect()
        await message.channel.send('입장')
    if message.content.find('@퇴장') > -1:
        await client.voice_clients[0].disconnect()
        await message.channel.send('퇴장')
    if message.content.find('@재생') > -1:
        url = message.content.split(" ")[1]
        option = {
            'outtmpl' : "file/" + url.split('=')[1] + ".mp3"
        }
        with YoutubeDL(option) as ydl :
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            title = info["title"]
        client.voice_clients[0].play(FFmpegPCMAudio("file/" + url.split('=')[1] + ".mp3"))
        

client.run("ODcxNzMwMDI3ODc0NjM1Nzk3.YQfj2g.5nm_WQyv2iN06aZS2W_Ac8JLAuA")