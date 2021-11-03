async def display_help(ctx):
    help_message = "Welcome to AFK Player <Beta>!:musical_note: :smile:\n" \
                   "*[The music bot currently only supports Youtube links]*\n" \
                   "\t:arrow_forward: **!play <keywords | link>**\n"\
                   "\t\tPlay song from [keywords] or [youtube-link]\n" \
                   "\t\tThis command will override whatever is next in the song queue\n" \
                   "\t\twhile keeping the queue in the same state.\n" \
                   "\n" \
                   "\t:koko: **!queue <keywords | link>**\n" \
                   "\t\tAdd a song to the queue from [keywords] or [youtube-link]\n" \
                   "\t\tThe song will automatically play once the previous song has ended.\n" \
                   "\n" \
                   "\t:fast_forward: **!skip**\n" \
                   "\t\tSkip the to the next song that's in the song queue.\n" \
                   "\t\tIf the queue is empty, nothing will happen.\n" \
                   "\n" \
                   "\t:notes: **!show**\n" \
                   "\t\tShow the current state of the songs queue.\n" \
                   "\n" \
                   "\t:musical_note: **!info**\n" \
                   "\t\tShow info about the currently playing song.\n" \
                   "\n" \
                   "\t:arrow_right: **!playfrom <seconds>**\n" \
                   "\t\tPlay current song starting from [seconds].\n" \
                   "\t\tThe input seconds act as an offset from the start of the song,\n" \
                   "\t\tand **NOT** from the current time.\n" \
                   "\n" \
                   "\t:pause_button: **!pause**\n" \
                   "\t\tPause the song that is currently playing,\n" \
                   "\t\twithout changing the state of the song queue.\n" \
                   "\n" \
                   "\t:stop_button: **!stop**\n" \
                   "\t\tStop the song that is currently playing,\n" \
                   "\t\tand clear the song queue completely.\n" \
                   "\t\t*NOTE: DO NOT CONFUSE WITH !PAUSE*\n" \
                   "\n" \
                   "\t:play_pause: **!resume**\n" \
                   "\t\tResume the song that was previously paused.\n" \
                   "\t\tThis command will only work after using the !pause command.\n" \
                   "\t\tThis command will not work after using the !stop command\n" \
                   "\n" \
                   "\t:woman_tipping_hand: **!help**\n" \
                   "\t\tDisplay this help message! :wave:\n" \
                   "\n" \

    await ctx.send(help_message)
