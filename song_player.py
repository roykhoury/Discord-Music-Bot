import asyncio
from collections import deque

from discord import FFmpegPCMAudio
from discord.utils import get
from youtube_dl import YoutubeDL

import constants


class SongPlayer:
    def __init__(self):
        self.song_queue = deque()
        self.current_song = {}

    def _play_next(self, ctx, bot):
        if len(self.song_queue) <= 0:
            return

        # Get voice and check is already playing, stop it before playing the next source
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.pause()

        # Remove song from queue, and play it
        song = self.song_queue.pop()
        player = FFmpegPCMAudio(song['url'], **constants.ffmpeg_options)
        voice.play(player, after=lambda e: self._play_next(ctx, bot))

        # Set current song, and return message to user
        self.current_song = {'song': song }
        send_message = ctx.send('Playing {0}'.format(song['title']))
        asyncio.run_coroutine_threadsafe(send_message, bot.loop)

    async def _get_song(self, source):
        # Download url or from keywords
        with YoutubeDL(constants.ydl_options) as ydl:
            info = ydl.extract_info(source, download=False)

        if info is None:
            raise RuntimeError('Couldn\'t find anything that matches `{}`'.format(source))

        if 'entries' in info:
            info = info['entries'][0]

        return info

    async def play(self, ctx, source, bot):
        song_info = await self._get_song(source)

        # Append song to queue
        self.song_queue.append({
            'url': song_info['formats'][0]['url'],
            'title': song_info['title'],
            'tags': song_info['tags'],
            'duration': song_info['duration']
        })

        self._play_next(ctx, bot)

    async def queue(self, ctx, source):
        song_info = await self._get_song(source)

        # Append song to queue
        self.song_queue.appendleft({
            'url': song_info['formats'][0]['url'],
            'title': song_info['title'],
            'tags': song_info['tags'],
            'duration': song_info['duration']
        })

        await ctx.send('Adding to queue {0}'.format(song_info['title']))

    async def skip(self, ctx, bot):
        if len(self.song_queue) <= 0:
            await ctx.send('There is no next song to skip to!')
            return

        self._play_next(ctx, bot)

    async def show(self, ctx):
        if len(self.song_queue) <= 0:
            await ctx.send('Queue is empty!')
            return

        message = ''
        for song in self.song_queue:
            message += '- [' + song['title'] + '] \n'
        await ctx.send(message.format())

    async def offset(self, ctx, bot, seconds):
        voice = get(bot.voice_clients, guild=ctx.guild)
        if not voice or not voice.is_playing():
            await ctx.send('Nothing playing right now!')
            return

        # If playing, pause it so that we can play from the next timestamp
        if voice and voice.is_playing():
            voice.pause()

        # make a new player from the new timestamp
        duration = min(seconds, self.current_song['song']['duration'], 0)
        ffmpeg_options = {
            'before_options': constants.ffmpeg_options['before_options'] + ' -ss ' + str(duration),
            'options': constants.ffmpeg_options['options']
        }

        # play from new timestamp
        player = FFmpegPCMAudio(self.current_song['song']['url'], **ffmpeg_options)
        voice.play(player, after=lambda e: self._play_next(ctx, bot))

        await ctx.send('Playing from: {0} seconds'.format(duration))

    async def pause(self, ctx, bot):
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.pause()
            await ctx.send('Paused!')
        else:
            await ctx.send('Nothing playing right now!')

    async def stop(self, ctx, bot):
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.stop()
            await ctx.send('Stopped, and cleared queue')
        else:
            await ctx.send('Nothing playing right now!')

    async def resume(self, ctx, bot):
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and not voice.is_playing():
            voice.resume()
            await ctx.send('Resuming!')
        else:
            await ctx.send('Nothing paused right now!')
