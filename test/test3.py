from asyncio.windows_events import NULL
import re
from discord.embeds import Embed
from discord.ext import commands
from discord.player import FFmpegPCMAudio
from youtube_dl.YoutubeDL import YoutubeDL 

client = commands.Bot(command_prefix='*')

queues = {}
musiclist = {}

global confirmYn
confirmYn = True

async def add_queue(ctx, url):
    url1 = re.match('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', url) #정규 표현식을 사용해 url 검사
    if url1 == None:
        await ctx.send(embed=Embed(title=":no_entry_sign: url을 제대로 입력해주세요."))
        return
    ydl_opts = {'format': 'bestaudio'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
    player = FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)

    if ctx.guild.id in queues:
        queues[ctx.guild.id].append(player)
        musiclist[ctx.guild.id].append(url)
    else:
        queues[ctx.guild.id] = [player]
        musiclist[ctx.guild.id] = [url]

def check_queue(id):
    if queues[id] != []:
        voice = client.voice_clients[0]
        voice.play(queues[id].pop(0))
        musiclist[id].pop(0)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

async def joinCheck(ctx, type):
    if client.voice_clients == []:
        await ctx.author.voice.channel.connect()
    elif client.voice_clients[0].channel != ctx.author.voice.channel: 
        titleMsg = str(client.voice_clients[0].channel) + " 채널에 연결되어 있습니다."
        descriptionMsg = str(client.voice_clients[0].channel) + " 채널과의 연결을 끊고 " + str(ctx.author.voice.channel) + " 채널에 연결하시겠습니까?"
        embed = Embed(title = titleMsg, description = descriptionMsg)
        embed.add_field(name="YES", value="⭕")
        embed.add_field(name="NO", value="❌")
        msg = await ctx.send(embed=embed)
        global confirmYn
        confirmYn = False
        await msg.add_reaction("⭕")
        await msg.add_reaction("❌")
    elif client.voice_clients[0].channel == ctx.author.voice.channel and type =="join": 
        await ctx.send(embed=Embed(title="이미 " + str(ctx.author.voice.channel) + " 채널에 연결되어있습니다."))

@client.event
async def on_reaction_add(reaction, user):
    global confirmYn
    if user.bot == 1:
        return None
    if confirmYn:
        return None
    await reaction.message.remove_reaction("⭕", client.user)
    await reaction.message.remove_reaction("❌", client.user)
    if str(reaction.emoji) == "⭕":
        titleMsg = "⭕를 선택하셨습니다. \n" + str(client.voice_clients[0].channel) + " 채널과의 연결을 끊고 " + str(user.voice.channel) + " 채널에 연결합니다."
        await reaction.message.channel.send(embed=Embed(title = titleMsg))
        await client.voice_clients[0].disconnect()
        await user.voice.channel.connect()
    if str(reaction.emoji) == "❌":
        titleMsg = "❌를 선택하셨습니다. \n" + str(client.voice_clients[0].channel) + " 채널과의 연결을 유지합니다."
        await reaction.message.channel.send(embed=Embed(title = titleMsg))
        await reaction.message.remove_reaction("⭕", client.user)
        await reaction.message.remove_reaction("❌", client.user)
    confirmYn = True

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.command()
async def hi(ctx):
    await ctx.send(embed=Embed(title="안녕",url ="http://google.com"))

@client.command()
async def join(ctx):
    await joinCheck(ctx, "join")

@client.command()
async def leave(ctx):
    await client.voice_clients[0].disconnect()
    print(client.voice_clients)

@client.command()
async def play(ctx, url):
    await joinCheck(ctx, "play")
    await add_queue(ctx, url)

    if queues[ctx.guild.id] != []:
        voice = client.voice_clients[0]
        voice.play(queues[ctx.guild.id].pop(0))
        await ctx.send("PLAY : " + musiclist[ctx.guild.id].pop(0))
    else :
        await ctx.send("예약 된 노래가 없습니다.")

@client.command()
async def stop(ctx):
    if client.voice_clients[0].is_playing():
        client.voice_clients[0].stop()
    else:
        await ctx.send("재생 중인 노래가 없습니다.")

@client.command()
async def pause(ctx):
    if client.voice_clients[0].is_playing():
        client.voice_clients[0].pause()
    else:
        await ctx.send("재생 중인 노래가 없습니다.")

@client.command()
async def resume(ctx):
    if client.voice_clients[0].is_paused:
        client.voice_clients[0].resume()
    else:
        await ctx.send("일시정지 상태가 아닙니다.")

@client.command()
async def queue(ctx, url):
    await add_queue(ctx, url)

@client.command()
async def list(ctx):
    embed = embed(
        title='대기중인 곡 들',
        description='대기중.....'
    )
    for i in musiclist[ctx.guild.id]:
        print('예약리스트 : ' + i)
        embed.add_field(name='대기중인 곡', value=i, inline=False)
    await ctx.send(embed=embed)

client.run('ODcxNzMwMDI3ODc0NjM1Nzk3.YQfj2g.5nm_WQyv2iN06aZS2W_Ac8JLAuA')