import asyncio
from asyncio.windows_events import NULL
import json
import re
from time import sleep
from discord.ext import commands
from gtts import gTTS
import youtube_dl
from youtubesearchpython import *
import discord
import random

client = commands.Bot(command_prefix="!", help_command=None, intents=discord.Intents.all())

playlist = {}
playlistTitle = {}
playLoop = {}
playRandom = {}
nowSong = {}
nowUrl = {}

async def songStart(ctx, voice):
    server = ctx.guild.id
    if not voice.is_playing() and not voice.is_paused():
        ydl_opts = {"format": "bestaudio"}
        FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if not playLoop[server]:
                if playRandom[server]:
                    num = random.randrange(0,len(playlist[server])-1)
                    nowUrl[server] = playlist[server].pop(num)
                    nowSong[server] = playlistTitle[server].pop(num)
                else:
                    nowUrl[server] = playlist[server].pop(0)
                    nowSong[server] = playlistTitle[server].pop(0)
            info = ydl.extract_info(nowUrl[server], download=False)
            URL = info["formats"][0]["url"]
        voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    while voice.is_playing() or voice.is_paused():
        await asyncio.sleep(0.5)

@client.command()
async def tts(ctx, msg):
    server = ctx.guild.id
    if ctx.author.voice is None:
        await ctx.send(embed=discord.Embed(title="연결 된 음성 채널이 없습니다."))
    else:
        channel = ctx.author.voice.channel
        if client.voice_clients == []:
            playLoop[server] = False
            playRandom[server] = False
            await channel.connect()
        else:
            serverCheck = False
            for voice_client in client.voice_clients:
                if voice_client.guild.id == server:
                    if channel != voice_client.channel:
                        titleMsg = str(voice_client.channel) + " 채널에 연결되어 있습니다."
                        await ctx.send(embed=discord.Embed(title=titleMsg))
                        return
                    else:
                        serverCheck = True
            if not serverCheck:
                playLoop[server] = False
                playRandom[server] = False
                await channel.connect()
        for voice_client in client.voice_clients:
            if voice_client.guild.id == server:
                voice =  voice_client
        if(voice.is_playing()):
            await ctx.send(embed=discord.Embed(title="재생 중인 파일이 있습니다."))
        else:
            tts = gTTS(text=msg, lang="ko")
            tts.save("./tts.mp3")
            voice.play(discord.FFmpegPCMAudio(source="./tts.mp3"))
        
@client.command()
async def p(ctx, msg):
    server = ctx.guild.id
    if ctx.author.voice is None:
        await ctx.send(embed=discord.Embed(title="연결 된 음성 채널이 없습니다."))
    else:
        channel = ctx.author.voice.channel
        if client.voice_clients == []:
            playLoop[server] = False
            playRandom[server] = False
            await channel.connect()
        else:
            serverCheck = False
            for voice_client in client.voice_clients:
                if voice_client.guild.id == server:
                    if channel != voice_client.channel:
                        titleMsg = str(voice_client.channel) + " 채널에 연결되어 있습니다."
                        await ctx.send(embed=discord.Embed(title=titleMsg))
                        return
                    else:
                        serverCheck = True
            if not serverCheck:
                playLoop[server] = False
                playRandom[server] = False
                await channel.connect()
        videos = VideosSearch(msg, limit = 1, language = "ko", region = "KR").result()["result"]
        if len(videos) == 1:
            video = videos[0]
            if server in playlist:
                playlist[server].append(video["link"])
                playlistTitle[server].append(video["title"])
            else:
                playlist[server] = [video["link"]]
                playlistTitle[server] = [video["title"]]
            await ctx.send(embed=discord.Embed(title="노래 추가",description=video["title"]))
        elif re.search(r"(?<=list=)([a-zA-Z0-9+/=_-]+)", msg) != None:
            list = Playlist(msg)
            for video in list.videos:
                if server in playlist:
                    playlist[server].append(video["link"].split("&list=")[0])
                    playlistTitle[server].append(video["title"])
                else:
                    playlist[server] = [video["link"].split("&list=")[0]]
                    playlistTitle[server] = [video["title"]]
            await ctx.send(embed=discord.Embed(title="플레이리스트 추가",description=list.info["info"]["title"]))
        for voice_client in client.voice_clients:
            if voice_client.guild.id == server:
                voice =  voice_client
        if not voice.is_playing() and not voice.is_paused():
            while True:
                await songStart(ctx, voice)
                if ((server in playlist) and 0 < len(playlist[server])) or ((server in playLoop) and playLoop[server]):
                    continue
                break
            if server in nowSong:
                del nowSong[server]

@client.command()
async def c(ctx, msg=""):
    server = ctx.guild.id
    for voice_client in client.voice_clients:
            if voice_client.guild.id == server:
                voice =  voice_client
    if(msg == ""):
        if voice.is_playing():
            if playLoop[server]:
                playLoop[server] = False
                await ctx.send(embed=discord.Embed(title="반복 재생 종료"))
            else:
                voice.stop()
                await ctx.send(embed=discord.Embed(title="재생 취소",description=nowSong[server]))
        else:
            await ctx.send(embed=discord.Embed(title="재생 중인 노래가 없습니다."))
    elif (msg > 0):
        if (msg > len(playlist[server])):
            await ctx.send(embed=discord.Embed(title=str(msg) + "번에 해당하는 예약곡이 없습니다."))
        else:
            playlist[server].pop(msg-1)
            deleteSong = playlistTitle[server].pop(msg-1)
            await ctx.send(embed=discord.Embed(title="예약 취소",description=str(msg) + ". " + deleteSong))
    else:
        await ctx.send(embed=discord.Embed(title="잘못된 명령인수입니다."))

@client.command()
async def list(ctx):
    server = ctx.guild.id
    if server in playlistTitle:
        if 0 < len(playlistTitle[server]):
            list = ""
            num = 0
            for i in playlistTitle[server]:
                num += 1
                list += str(num) + ". " + i + "\n"
            await ctx.send(embed=discord.Embed(title="예약 목록",description=list))   
        else:
            await ctx.send(embed=discord.Embed(title="예약 목록이 없습니다.")) 
    else:
        await ctx.send(embed=discord.Embed(title="예약 목록이 없습니다."))

@client.command()
async def now(ctx):
    server = ctx.guild.id
    if server in nowSong:
        await ctx.send(embed=discord.Embed(title="Now Playing",description=nowSong[server]))
    else:
        await ctx.send(embed=discord.Embed(title="재생 중인 노래가 없습니다."))

@client.command()
async def kick(ctx):
    server = ctx.guild.id
    if server in playlist:
        del playlist[server]
    if server in playlistTitle:
        del playlistTitle[server]
    if server in playLoop:
        del playLoop[server]
    if server in playRandom:
        del playRandom[server]
    if server in nowSong:
        del nowSong[server]
    if server in nowUrl:
        del nowUrl[server]
    for voice_client in client.voice_clients:
        if voice_client.guild.id == server:
            await voice_client.disconnect()

@client.command()
async def loop(ctx):
    server = ctx.guild.id
    if server in nowSong:
        if not playLoop[server]:
            playLoop[server] = True
            await ctx.send(embed=discord.Embed(title="반복 재생 시작"))
        else:
            await ctx.send(embed=discord.Embed(title="이미 반복 재생 중입니다."))
    else:
        await ctx.send(embed=discord.Embed(title="재생 중인 노래가 없습니다."))

@client.command()
async def 랜덤(ctx):
    server = ctx.guild.id
    if server in playlist:
        if 0 < len(playlist[server]):
            if not playRandom[server]:
                playRandom[server] = True
                await ctx.send(embed=discord.Embed(title="랜덤 재생 시작"))
            else:
                await ctx.send(embed=discord.Embed(title="이미 랜덤 재생 중입니다."))
        else:
            await ctx.send(embed=discord.Embed(title="예약 목록이 없습니다."))
    else:
        await ctx.send(embed=discord.Embed(title="예약 목록이 없습니다."))

@client.command()
async def 랜덤취소(ctx):
    server = ctx.guild.id
    if playRandom[server]:
        playRandom[server] = False
        await ctx.send(embed=discord.Embed(title="랜덤 재생 종료"))
    else:
        await ctx.send(embed=discord.Embed(title="랜덤 재생 중이 아닙니다."))

@client.command()
async def help(ctx):
    list = ""
    list += "!p: 노래 재생 또는 예약 \n"
    list += "!c: 반복 재생 취소, 재생 중인 노래 취소, 예약된 노래 취소 (ex. ;c 1 = 1번 예약곡 취소)\n"
    list += "!list: 예약 된 노래 목록 확인 \n"
    list += "!now: 현재 재생 중인 노래 확인 \n"
    list += "!kick: 봇 강제 퇴장 및 초기화\n"
    list += "!loop: 반복 재생\n"
    list += "!랜덤: 무작위 순서로 노래 재생\n"
    list += "!랜덤취소: 무작위 순서로 노래 재생 취소 (순차 재생)\n"
    list += "!tts: 음성합성기능"
    await ctx.send(embed=discord.Embed(title="명령어 목록",description=list))   

@client.event
async def on_message(msg):
    if msg.author != client.user:
        server = msg.guild.name
        channel = msg.channel.name
        writer = msg.author.name + "#" + msg.author.discriminator
        message = msg.content
        log.info(server + " | " + channel + " | " + writer + " | " + message)
        await client.process_commands(msg)

with open('config.json') as f :
    config = json.load(f)

client.run(config['token'])