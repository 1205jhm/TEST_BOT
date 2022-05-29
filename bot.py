import asyncio
from discord.ext import commands
import youtube_dl
import discord
import random

client = commands.Bot(command_prefix=';', help_command=None)

playlist = {}
playRoop = {}
playRandom = {}
nowSong = {}

async def songStart(ctx, voice):
    server = ctx.guild.id
    if not voice.is_playing() and not voice.is_paused():
        ydl_opts = {'format': 'bestaudio'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if not playRoop[server]:
                if playRandom[server]:
                    num = random.randrange(0,len(playlist[server])-1)
                    nowSong[server] = playlist[server].pop(num)
                else:
                    nowSong[server] = playlist[server].pop(0)
            info = ydl.extract_info(nowSong[server], download=False)
            URL = info['formats'][0]['url']
        voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    while voice.is_playing() or voice.is_paused():
        await asyncio.sleep(0.1)

@client.command()
async def p(ctx, url):
    server = ctx.guild.id
    if ctx.author.voice is None:
        await ctx.send(embed=discord.Embed(title='연결 된 음성 채널이 없습니다.'))
    else:
        channel = ctx.author.voice.channel
        if client.voice_clients == []:
            playRoop[server] = False
            playRandom[server] = False
            await channel.connect()
        elif channel != client.voice_clients[0].channel:
            titleMsg = str(client.voice_clients[0].channel) + " 채널에 연결되어 있습니다."
            await ctx.send(embed=discord.Embed(title=titleMsg))
            return
        if server in playlist:
            playlist[server].append(url)
        else:
            playlist[server] = [url]
        await ctx.send(embed=discord.Embed(title='노래 추가',description=url))
        voice = client.voice_clients[0]
        if not voice.is_playing() and not voice.is_paused():
            while True:
                await songStart(ctx, voice)
                if 0 < len(playlist[server]) or playRoop[server]:
                    continue
                break
            del nowSong[server]

@client.command()
async def c(ctx):
    server = ctx.guild.id
    if client.voice_clients[0].is_playing():
        if playRoop[server]:
            playRoop[server] = False
            await ctx.send(embed=discord.Embed(title='반복 재생 종료'))
        else:
            client.voice_clients[0].stop()
            await ctx.send(embed=discord.Embed(title='재생 취소',description=nowSong[server]))
    else:
        await ctx.send(embed=discord.Embed(title='재생 중인 노래가 없습니다.'))

@client.command()
async def l(ctx):
    server = ctx.guild.id
    if server in playlist:
        if 0 < len(playlist[server]):
            list = ""
            for i in playlist[server]:
                list += i
                list += "\n"
            await ctx.send(embed=discord.Embed(title='예약 목록',description=list))   
        else:
            await ctx.send(embed=discord.Embed(title='예약 목록이 없습니다.')) 
    else:
        await ctx.send(embed=discord.Embed(title='예약 목록이 없습니다.'))

@client.command()
async def kick(ctx):
    server = ctx.guild.id
    if server in playlist:
        del playlist[server]
    if server in playRoop:
        del playRoop[server]
    if server in playRandom:
        del playRandom[server]
    if server in nowSong:
        del nowSong[server]
    await client.voice_clients[0].disconnect()

@client.command()
async def re(ctx):
    server = ctx.guild.id
    if server in nowSong:
        if not playRoop[server]:
            playRoop[server] = True
            await ctx.send(embed=discord.Embed(title='반복 재생 시작'))
        else:
            await ctx.send(embed=discord.Embed(title='이미 반복 재생 중입니다.'))
    else:
        await ctx.send(embed=discord.Embed(title='재생 중인 노래가 없습니다.'))

@client.command()
async def 랜덤(ctx):
    server = ctx.guild.id
    if server in playlist:
        if 0 < len(playlist[server]):
            if not playRandom[server]:
                playRandom[server] = True
                await ctx.send(embed=discord.Embed(title='랜덤 재생 시작'))
            else:
                await ctx.send(embed=discord.Embed(title='이미 랜덤 재생 중입니다.'))
        else:
            await ctx.send(embed=discord.Embed(title='예약 목록이 없습니다.'))
    else:
        await ctx.send(embed=discord.Embed(title='예약 목록이 없습니다.'))

@client.command()
async def 랜덤취소(ctx):
    server = ctx.guild.id
    if playRandom[server]:
        playRandom[server] = False
        await ctx.send(embed=discord.Embed(title='랜덤 재생 종료'))
    else:
        await ctx.send(embed=discord.Embed(title='랜덤 재생 중이 아닙니다.'))

@client.command()
async def help(ctx):
    list = ""
    list += ";p : 노래 재생 또는 예약 \n"
    list += ";c : 반복 재생 취소 또는 재생 중인 노래 취소 \n"
    list += ";l : 예약 된 노래 목록 확인 \n"
    list += ";kick : 봇 강제 퇴장 및 초기화\n"
    list += ";re : 반복 재생\n"
    list += ";랜덤 : 무작위 순서로 노래 재생\n"
    list += ";랜덤취소 : 무작위 순서로 노래 재생 취소 (순차 재생)\n"
    await ctx.send(embed=discord.Embed(title='명령어 목록',description=list))   

client.run('ODcxNzMwMDI3ODc0NjM1Nzk3.YQfj2g.5nm_WQyv2iN06aZS2W_Ac8JLAuA')