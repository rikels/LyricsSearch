LyricsSearch
============

The Viewlyrics part is a translated Python script to lookup lyrics from viewlyrics.
The original Viewlyrics script was written in PHP by PedroHLC, I just converted it to Python for use in other Python scripts.
The original script can be found here: https://github.com/PedroHLC/ViewLyricsOpenSearcher

This script can be used as a module to import to your own script!
Don't forget to take a look in the Wiki, it could help you out!

you have to place the module into your current directory, or in a python root dir
Import lyrics

lyrics = lyrics.MiniLyrics("Queen","Bohemian rhapsody")
Will return a dictionary with data from viewlyrics.com. Like the url to download a lyric, the rating, artist and title.
lyrics[0] will include the first result, lyrics[1] will be the second...
The returned results are ordered by rating (highest first).


lyrics.LyricWikia("Queen","Bohemian rhapsody")
Will return the lyric as it is shown on lyrics.wikia.com as a string.