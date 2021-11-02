import os

from discord.ext import commands
from song_player import SongPlayer

import constants

bot = commands.Bot(command_prefix=constants.prefix)
song_player = SongPlayer()


@bot.event
async def on_ready():
    print('Bot is online: {0}'.format(bot.user))


@bot.command(pass_context=True)
async def play(ctx, *, source):
    await song_player.play(ctx, source, bot)


@bot.command(pass_context=True)
async def queue(ctx, *, source):
    await song_player.queue(ctx, source)


@bot.command(pass_context=True)
async def skip(ctx):
    await song_player.skip(ctx, bot)


@bot.command(pass_context=True)
async def show(ctx):
    await song_player.show(ctx)


@bot.command(pass_context=True)
async def info(ctx):
    await song_player.info(ctx)


@bot.command(pass_context=True)
async def playfrom(ctx, seconds):
    await song_player.play_from(ctx, bot, int(seconds))


@bot.command(pass_context=True)
async def pause(ctx):
    await song_player.pause(ctx, bot)


@bot.command(pass_context=True)
async def stop(ctx):
    await song_player.stop(ctx, bot)


@bot.command(pass_context=True)
async def resume(ctx):
    await song_player.resume(ctx, bot)


@pause.error
@play.error
@resume.error
@show.error
@playfrom.error
@queue.error
@skip.error
@stop.error
@show.error
async def on_error(ctx, error):
    # if error is no channel found, return a msg to user
    if not ctx.message.author.voice:
        await ctx.send('{0}, connect to a channel first!'.format(ctx.message.author.mention))
        return

    # Other unknown error
    msg = 'Command failed from {0}\n' \
          'Error: {1}\n'.format(ctx.message.author.mention, error)
    await ctx.send(msg)


@bot.before_invoke
async def common(ctx):
    # connect to voice chat if not already
    if not ctx.guild.voice_client and ctx.message.author.voice:
        voice_channel = ctx.message.author.voice.channel
        await voice_channel.connect()

    # Make it look like the bot is typing ;)
    await ctx.trigger_typing()


bot.run(os.getenv('TOKEN'))
