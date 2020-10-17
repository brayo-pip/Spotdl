#! Basic necessities to get the CLI running
from spotdl.search.spotifyClient import initialize
#! Song Search from different start points
from spotdl.search.utils import get_playlist_tracks, get_album_tracks, search_for_song
from spotdl.search.songObj import SongObj

#! The actual download stuff
from spotdl.download.downloader import DownloadManager

#! to avoid packaging errors
from multiprocessing import freeze_support
import os
import time


#! Usage is simple - call 'python __main__.py <links, search terms, tracking files seperated by spaces>
#! Eg.
#!      python __main__.py https://open.spotify.com/playlist/37i9dQZF1DWXhcuQw7KIeM?si=xubKHEBESM27RqGkqoXzgQ 'old gods of asgard Control' https://open.spotify.com/album/2YMWspDGtbDgYULXvVQFM6?si=gF5dOQm8QUSo-NdZVsFjAQ https://open.spotify.com/track/08mG3Y1vljYA6bvDt4Wqkj?si=SxezdxmlTx-CaVoucHmrUA
#!
#! Well, yeah its a pretty long example but, in theory, it should work like a charm.
#!
#! A '.spotdlTrackingFile' is automatically  created with the name of the first song in the playlist/album or
#! the name of the song supplied. We don't really re re re-query YTM and SPotify as all relevant details are
#! stored to disk.
#!
#! Files are cleaned up on download failure.
#!
#! All songs are normalized to standard base volume. the soft ones are made louder, the loud ones, softer.
#!
#! The progress bar is synced across multiple-processes (4 processes as of now), getting the progress bar to
#! sync was an absolute pain, each process knows how much 'it' progressed, but the display has to be for the
#! overall progress so, yeah... that took time.
#!
#! spotdl will show you its true speed on longer download's - so make sure you try downloading a playlist.
#!
#! still yet to try and package this but, in theory, there should be no errors.
#!
#!                                                          - cheerio! (Michael)
#!
#! P.S. Tell me what you think. Up to your expectations?

#! Script Help
help_notice = """
To download a song run,
    spotdl $trackUrl
    eg. spotdl https://open.spotify.com/track/08mG3Y1vljYA6bvDt4Wqkj?si=SxezdxmlTx-CaVoucHmrUA

    spotdl $trackUri
    eg. spotdl spotify:track:08mG3Y1vljYA6bvDt4Wqkj

To download a album run,
    spotdl $albumUrl
    eg. spotdl https://open.spotify.com/album/2YMWspDGtbDgYULXvVQFM6?si=gF5dOQm8QUSo-NdZVsFjAQ

    spotdl $albumUri
    eg. spotdl spotify:album:2YMWspDGtbDgYULXvVQFM6

To download a playlist run,
    spotdl $playlistUrl
    eg. spotdl https://open.spotify.com/playlist/37i9dQZF1DWXhcuQw7KIeM?si=xubKHEBESM27RqGkqoXzgQ

To download a playlist run,
    spotdl $playlistUri
    eg. spotdl spotify:playlist:37i9dQZF1DWXhcuQw7KIeM

To search for and download a song (not very accurate) run,
    spotdl $songQuery
    eg. spotdl 'The HU - Sugaan Essenna'

To resume a failed/incomplete download run,
    spotdl $pathToTrackingFile
    eg. spotdl 'Sugaan Essenna.spotdlTrackingFile'

    Note, '.spotDlTrackingFiles' are automatically created during download start, they are deleted on
    download completion

You can chain up download tasks by seperating them with spaces:
    spotdl $songQuery1 $albumUrl $songQuery2 ... (order does not matter)
    eg. spotdl 'The Hu - Sugaan Essenna' https://open.spotify.com/playlist/37i9dQZF1DWXhcuQw7KIeM?si=xubKHEBESM27RqGkqoXzgQ ...

Spotdl downloads up to 4 songs in parallel - try to download albums and playlists instead of
tracks for more speed
"""
start = time.time()
cliArgs = os.sys.argv

def console_entry_point():
    """
    This is where all the console processing magic happens.
    Its super simple, rudimentary even but, it's dead simple & it works.
    """

    if "--help" in cliArgs or "-h" in cliArgs:
        print(help_notice)

        #! We use 'return None' as a convenient exit/break from the function
        return None

    initialize(
        clientId="4fe3fecfe5334023a1472516cc99d805",
        clientSecret="0f02b7c483c04257984695007a4a8d5c",
    )

    downloader = DownloadManager()

    for request in cliArgs[1:]:
        if "?" in request:
            # strip unnecessary data for both url and uri
            # e.g https://open.spotify.com/track/4Q34FP1AT7GEl9oLgNtiWj?context=spotify%3Aplaylist%3A37i9dQZF1DXcBWIGoYBM5M&si=DlMAsJ5pSD6tdUSn2XqB0g
            # becomes https://open.spotify.com/track/4Q34FP1AT7GEl9oLgNtiWj
            # e.g spotify:track:4Q34FP1AT7GEl9oLgNtiWj?context=spotify%3Aplaylist%3A37i9dQZF1DXcBWIGoYBM5M
            # becomes spotify:track:4Q34FP1AT7GEl9oLgNtiWj

            request = request[: request.find("?")]
        if "open.spotify.com" in request:
            # it's a url
            if "track" in request:
                print("Fetching Song...")
                song = SongObj.from_url(request)

                if song.get_youtube_link() != None:
                    downloader.download_single_song(song)
                else:
                    print(
                        f"Skipping {song.get_song_name()} ({request}) as no match could be found on youtube"
                    )

            elif "album" in request:
                print("Fetching Album...")
                songObjList = get_album_tracks(request)

                downloader.download_multiple_songs(songObjList)

            elif "playlist" in request:
                print("Fetching Playlist...")
                songObjList = get_playlist_tracks(request)
                # print(f"Fetching took {time.time()-start} seconds")
                downloader.download_multiple_songs(songObjList)
        elif "spotify:" in request:
            # it's a URI with format Spotify:...:ID
            if "track:" in request:
                print("Fetching Song...")
                # yes, passing a URI to this function still works coz it relies on another
                # spotipy function that simply extracts the ID, ideally u can just pass the ID
                # and the track downloads
                song = SongObj.from_url(request)

                if song.get_youtube_link() != None:
                    downloader.download_single_song(song)
                else:
                    print(
                        f"Skipping {song.get_song_name()} ({request}) as no match could be found on youtube"
                    )

            elif "album:" in request:
                print("Fetching Album...")
                songObjList = get_album_tracks(request)

                downloader.download_multiple_songs(songObjList)

            elif "playlist:" in request:
                print("Fetching Playlist...")
                songObjList = get_playlist_tracks(request)

                downloader.download_multiple_songs(songObjList)

        elif request.endswith(".spotdlTrackingFile"):
            print("Preparing to resume download...")
            downloader.resume_download_from_tracking_file(request)

        else:
            print(f'Searching for song "{request}"...')
            try:
                song = search_for_song(request)
                downloader.download_single_song(song)

            except Exception:
                print(f'No song named "{request}" could be found on spotify')

    downloader.close()


if __name__ == "__main__":

    console_entry_point()
