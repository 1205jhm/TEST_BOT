import discord
import youtube_dl
from discord.ext import commands

client = commands.Bot(command_prefix='/')

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.command("p")
async def play(ctx, url):
    channel = ctx.author.voice.channel
    if client.voice_clients == []:
        await channel.connect()
        await ctx.send("connected to the voice channel, " + str(client.voice_clients[0].channel))

    ydl_opts = {'format': 'bestaudio'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
    voice = client.voice_clients[0]
    voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

client.run('ODczOTAzMzk2MzU1MjAzMTQz.YQ_L9g.0cFgo4EvRpagIcfQLslo6d2Kr1I') 



@client.command(brief="Plays a single video, from a youtube URL") #or bot.command()
async def play(ctx, url):
    voice = get(client.voice_clients, guild=ctx.guild)
    YDL_OPTIONS = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.%(ext)s',
    }

    with YoutubeDL(Music.YDL_OPTIONS) as ydl:
        ydl.download("URL", download=True)

    if not voice.is_playing():
        voice.play(FFmpegPCMAudio("song.mp3"))
        voice.is_playing()
        await ctx.send(f"Now playing {url}")
    else:
        await ctx.send("Already playing song")
        return


from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

@commands.command(brief="Plays a single video, from a youtube URL")
async def play(ctx, url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_link, download=False)
        URL = info['formats'][0]['url']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()
    else:
        await ctx.send("Already playing song")
        return