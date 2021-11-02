import asyncio
from collections import deque

from discord import FFmpegPCMAudio
from discord.utils import get
from youtube_dl import YoutubeDL

import constants


# static functions
def _to_minutes(total_seconds):
    hours = (total_seconds - (total_seconds % 3600)) / 3600
    seconds_minus_hours = (total_seconds - hours * 3600)
    minutes = (seconds_minus_hours - (seconds_minus_hours % 60)) / 60
    seconds = seconds_minus_hours - minutes * 60
    result = '{:02d}:'.format(int(hours)) if hours != 0 else ''
    result += '{:02d}:{:02d}'.format(int(minutes), int(seconds))
    return result


def _parse_song_info(song_info):
    song = {
        'url': song_info['formats'][0]['url'],
        'title': song_info['title'],
        'tags': song_info['tags'],
        'duration_min': _to_minutes(song_info['duration']),
        'duration_sec': song_info['duration']
    }
    return song


def _pretty_song_info(song_info):
    return '**{0}** [{1}]'.format(song_info['title'], song_info['duration_min'])


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
        # TODO: Switch to LAVALINK for better audio streaming quality
        song = self.song_queue.pop()
        player = FFmpegPCMAudio(song['url'], **constants.ffmpeg_options)
        voice.play(player, after=lambda e: self._play_next(ctx, bot))

        # Set current song, and return message to user
        self.current_song = {'song': song}
        send_message = ctx.send('🎶 Playing {}'.format(_pretty_song_info(song)))
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
        self.song_queue.append(_parse_song_info(song_info))
        self._play_next(ctx, bot)

    async def queue(self, ctx, source):
        song = await self._get_song(source)
        song = _parse_song_info(song)

        # Append song to queue
        self.song_queue.appendleft(song)
        await ctx.send('🎶 Adding to queue {0}'.format(_pretty_song_info(song)))

    async def skip(self, ctx, bot):
        if len(self.song_queue) <= 0:
            await ctx.send(':exclamation: There is no next song to skip to!')
            return

        self._play_next(ctx, bot)

    async def show(self, ctx):
        if len(self.song_queue) <= 0:
            await ctx.send(':exclamation: Queue is empty!')
            return

        message = ''
        for i, song in enumerate(self.song_queue):
            index = len(self.song_queue) - i
            message += '{0}. :musical_note: {1}\n'.format(index, _pretty_song_info(song))
        await ctx.send(message)

    async def play_from(self, ctx, bot, seconds):
        voice = get(bot.voice_clients, guild=ctx.guild)
        if not voice or not voice.is_playing():
            await ctx.send(':exclamation: Nothing playing right now!')
            return

        # If playing, pause it so that we can play from the next timestamp
        if voice and voice.is_playing():
            voice.pause()

        # make a new player from the new timestamp
        ffmpeg_options = {
            'before_options': constants.ffmpeg_options['before_options'] + ' -ss ' + str(seconds),
            'options': constants.ffmpeg_options['options']
        }

        # play from new timestamp
        player = FFmpegPCMAudio(self.current_song['song']['url'], **ffmpeg_options)
        voice.play(player, after=lambda e: self._play_next(ctx, bot))

        await ctx.send(':play_pause: Playing from: {0} seconds!'.format(seconds))

    async def pause(self, ctx, bot):
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.pause()
            await ctx.send(':pause_button: Paused!')
        else:
            await ctx.send(':exclamation: Nothing playing right now!')

    async def stop(self, ctx, bot):
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.stop()
            self.song_queue.clear()
            await ctx.send(':stop_button: Stopped, and cleared queue!')
        else:
            await ctx.send(':exclamation: Nothing playing right now!')

    async def resume(self, ctx, bot):
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and not voice.is_playing():
            voice.resume()
            await ctx.send(':musical_note: Resuming!')
        else:
            await ctx.send(':exclamation: Nothing paused right now!')

    async def info(self, ctx):
        if self.current_song:
            song = self.current_song['song']
            await ctx.send(':musical_note: Currently playing {0}'.format(_pretty_song_info(song)))
        else:
            await ctx.send(':exclamation: Nothing playing right now!')
