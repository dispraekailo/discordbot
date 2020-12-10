import discord
import json
import requests
import youtube_dl
import os
import random
from discord.ext import commands
from config import settings
from discord import Game
from ctypes.util import find_library
from discord import opus
import asyncio
from discord.voice_client import VoiceClient
from discord.ext.commands import Bot
from discord import utils
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system
Bot = commands.Bot(command_prefix='!')   # Провозглашаем переменную для бота с префиксом !

# Тут мы размещаем наши команды


client = discord.Client()
songs = asyncio.Queue()
play_next_song = asyncio.Event()

@Bot.command() # Не передаём аргумент pass_context, так как он был нужен в старых версиях.
async def hello(ctx): # Создаём функцию и передаём аргумент ctx.
    author = ctx.message.author # Объявляем переменную author и записываем туда информацию об авторе.

    await ctx.send(f'{author.mention}, Привет!') # Выводим сообщение с упоминанием автора, обращаясь к переменной author.
@Bot.command()
async def лиса(ctx):
    response = requests.get('https://some-random-api.ml/img/fox') # Get-запрос
    json_data = json.loads(response.text) # Извлекаем JSON
    author = ctx.message.author  # Объявляем переменную author и записываем туда информацию об авторе.
    embed = discord.Embed(color = 0xff9900, title = 'Держи лису') # Создание Embed'a
    embed.set_image(url = json_data['link']) # Устанавливаем картинку Embed'a
    await ctx.send(f'{author.mention}',embed = embed) # Отправляем Embed
@Bot.command()
async def собака(ctx):
    response = requests.get('https://some-random-api.ml/img/dog') # Get-запрос
    json_data = json.loads(response.text) # Извлекаем JSON
    author = ctx.message.author  # Объявляем переменную author и записываем туда информацию об авторе.
    embed = discord.Embed(color = 0xff9900, title = 'Держи собаку') # Создание Embed'a
    embed.set_image(url = json_data['link']) # Устанавливаем картинку Embed'a
    await ctx.send(f'{author.mention}',embed = embed) # Отправляем Embed
@Bot.command(pass_contention = True)
async def giverole(ctx, member: discord.Member, role = discord.Role):
 getrole = discord.utils.get(ctx.guild.roles, id = role )
 await member.add_roles(getrole)
@Bot.event
async def on_member_join(member):
    channel = client.get_channel(746179535837331479)
    role = discord.utils.get(member.guild.roles, name="test")
    await member.add_roles(role)
@Bot.command(pass_context = True)
async def test(ctx, member: discord.Member):
    role = discord.utils.get(member.guild.roles, name="test")
    await member.add_roles(role)
@Bot.command(pass_context = True)
async def untest(ctx, member: discord.Member):
    role = discord.utils.get(member.guild.roles, name="test")
    await member.remove_roles(role)
@Bot.event
async def on_raw_reaction_add(payload):
    if not payload.message_id == 784803672496406559:  # ID сообщения на которое нужно ставить реакции
        return
    if member := payload.member:
     if payload.emoji.id == 746643268586176524:  # или payload.emoji.name == "✔" для unicode-эмодзей
        await member.add_roles(member.guild.get_role(746643524212097134))
        await member.remove_roles(member.guild.get_role(746634235061862531))
     else:
        await member.add_roles(member.guild.get_role(746634235061862531))
        await member.remove_roles(member.guild.get_role(746643524212097134))




@Bot.command()
async def dsadas(ctx):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("Тебя ни в одном голосовом канале")
        return
    voice = get(Bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send("Подключился к серверу")
@Bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send("Отключился от сервера")


@Bot.command()
async def weather(ctx, *, city: str):
    api_key = "7f1e23163b47cbf21184f339f5c8eaf9"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    city_name = city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        async with ctx.typing():
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_celsiuis = str(round(current_temperature - 273.15))
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]
            weather_description = z[0]["description"]
            embed = discord.Embed(title=f"Weather in {city_name}",
                                  color=ctx.guild.me.top_role.color,
                                  timestamp=ctx.message.created_at, )
            embed.add_field(name="Descripition", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Температура(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
            embed.add_field(name="Влажность(%)", value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Атмосферное давление(мРт)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)

    else:
        print('error')
async def audio_player_task():
    while True:
        play_next_song.clear()
        current = await songs.get()
        current.start()
        await play_next_song.wait()


def toggle_next():
    client.loop.call_soon_threadsafe(play_next_song.set)
@Bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Музыка уже играет!")
        return

    await ctx.send("Ожидайте 5-10 секунд")

    voice = get(Bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"Сейчас играет: {nname[0]}")
    print("playing\n")
token = os.environ.get('BOT_TOKEN')

bot.run(str(token))
