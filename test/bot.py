from discord.ext import commands
from discord.player import FFmpegPCMAudio
from youtube_dl.YoutubeDL import YoutubeDL

client = commands.Bot(command_prefix='*')
que = {}
playerlist = {}
playlist = list()


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    if client.voice_clients == []:
        await channel.connect()
        await ctx.send("connected to the voice channel, " + str(client.voice_clients[0].channel))
    elif client.voice_clients[0].channel != channel: 
        if client.voice_clients[0].is_playing():
            client.voice_clients[0].pause()
        await client.voice_clients[0].disconnect()
        await channel.connect()
        client.voice_clients[0].resume()

@client.command()
async def play(ctx, url):
    channel = ctx.author.voice.channel
    if client.voice_clients == []:
        await channel.connect()
        await ctx.send("connected to the voice channel, " + str(client.voice_clients[0].channel))
    elif client.voice_clients[0].channel != channel: 
        if client.voice_clients[0].is_playing():
            client.voice_clients[0].pause()
        await client.voice_clients[0].disconnect()
        await channel.connect()
        client.voice_clients[0].resume()

    ydl_opts = {'format': 'bestaudio'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
    voice = client.voice_clients[0]
    voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

    

@client.command()
async def leave(ctx):
    await client.voice_clients[0].disconnect()

@client.command()
async def pause(ctx):
    if client.voice_clients[0].is_playing():
        client.voice_clients[0].pause()
    else:
        await ctx.send("already paused")

@client.command()
async def resume(ctx):
    if client.voice_clients[0].is_paused():
        client.voice_clients[0].resume()
    elif client.voice_clients[0].is_stopped(): 
        await ctx.send("노래가 없습니다")
    else:
        await ctx.send("already playing")
        

@client.command()
async def stop(ctx):
    if client.voice_clients[0].is_playing():
        client.voice_clients[0].stop()
    else:
        await ctx.send("not playing")

@client.command()
async def queue(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url)

client.run('ODcxNzMwMDI3ODc0NjM1Nzk3.YQfj2g.5nm_WQyv2iN06aZS2W_Ac8JLAuA')