prefix = '!'
ydl_options = {
    'format': 'bestaudio',
    'noplaylist': 'True',
    'default_search': 'ytsearch'
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': ['-vn']
}

