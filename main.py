import os
import asyncio

from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get
from youtube_dl import YoutubeDL

prefix = '!'
song_queue = []
bot = commands.Bot(command_prefix=prefix)
ydl_options = {'format': 'bestaudio', 'noplaylist': 'True', 'default_search': 'ytsearch', 'rm_cachedir': 'True'}
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': ['-vn']}


@bot.event
async def on_ready():
    print('Bot is online: {0}'.format(bot.user))


@bot.command(pass_context=True)
async def play(ctx, *, source):
    # connect to voice chat if not already
    if not ctx.guild.voice_client:
        voice_channel = ctx.message.author.voice.channel
        await voice_channel.connect()

    # Make it look like the bot is typing ;)
    async with ctx.typing():

        # Download url or playlist
        with YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(source, download=False)

        if 'entries' in info:
            song_info = info['entries'][0]
        else:
            song_info = info

        url = song_info['formats'][0]['url']
        title = song_info['title']

        # Append song to queue
        voice = get(bot.voice_clients, guild=ctx.guild)
        song_queue.append({'url': url, 'title': title})

        if voice.is_playing():
            await ctx.send('Adding to queue {0}'.format(title))
        else:
            play_next(ctx, voice)


def play_next(ctx, voice):
    if len(song_queue) <= 0:
        return

    try:
        song = song_queue.pop()
        player = FFmpegPCMAudio(song['url'], **ffmpeg_options)
        voice.play(player, after=lambda e: play_next(ctx, voice))
        send_message = ctx.send('Playing {0}'.format(song['title']))
        asyncio.run_coroutine_threadsafe(send_message, bot.loop)
    except:
        pass


@bot.command(pass_context=True)
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    play_next(ctx, voice)


@bot.command(pass_context=True)
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        await ctx.send('Paused!')
    else:
        await ctx.send('Nothing playing right now!')


@bot.command(pass_context=True)
async def stop(ctx):
    await pause.invoke(ctx)


@bot.command(pass_context=True)
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and not voice.is_playing():
        voice.resume()
        await ctx.send('Resuming!')
    else:
        await ctx.send('Nothing paused right now!')


@play.error
async def play_error(ctx, error):
    # if error is no channel found, return a msg to user
    if not ctx.message.author.voice:
        await ctx.send('Come on {0}, connect to a channel first!'.format(ctx.message.author.mention))
        return

    # Other unknown error
    msg = 'Command failed from {0}\n' \
          'Error: {1}\n'.format(ctx.message.author.mention, error)
    await ctx.send(msg)


bot.run(os.getenv('TOKEN'))
