from spotdl.search.songObj import SongObj
from spotdl.search.spotifyClient import initialize
from spotdl.lyrics.genius import Genius
initialize(
     clientId="4fe3fecfe5334023a1472516cc99d805",  
     clientSecret="0f02b7c483c04257984695007a4a8d5c",
 )

# g = Genius()

# print(g.from_query("A$ap Rocky", "j",lyric_fail=True))


s = SongObj.from_url('spotify:track:02kDW379Yfd5PzW5A6vuGt?context=spotify%3Aplaylist%3A37i9dQZF1DXcBWIGoYBM5M')
print(s.get_lyrics())

# print(Genius.from_query("Pop Smoke", "For The Night"))