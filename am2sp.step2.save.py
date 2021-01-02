import time

import spotipy
import spotipy.util
from spotipy.oauth2 import SpotifyClientCredentials

import _const
import _util

"""
Apple Musicで保存したアルバムを、Spotifyでも保存するようにします。
tsvファイルで指定したIDのアルバムをSpotifyに保存します。
apple-music.tsvに保存済みフラグをつけます。
"""

save_album_list_path = 'data/apple-music/save-albums.tsv'
apple_music_album_list_path = 'data/apple-music/apple-music-album-list.tsv'
unknown_album_list_path = 'data/apple-music/no-saved-albums.tsv'

user_id = _const.USER_ID
client_id = _const.CLIENT_ID
client_secret = _const.CLIENT_SECRET

token = spotipy.util.prompt_for_user_token(
    user_id,
    scope='user-library-modify',
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://127.0.0.1:8080/')
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(auth=token, client_credentials_manager=client_credentials_manager)

apple_music_album_list = _util.read_tsv(apple_music_album_list_path)
save_album_list = _util.read_tsv(save_album_list_path)

print(len(apple_music_album_list))
print(len(save_album_list))

apple_music_album_map = {}
for a in apple_music_album_list:
    if 'status' not in a:
        a['status'] = 'unknown'
    title = a.get('title')
    artist = a.get('artist')
    key = f'{title} / {artist}'
    apple_music_album_map[key] = a

for idx in range(0, len(save_album_list), 30):
    albums = save_album_list[idx:idx+30]
    album_ids = [x.get('id') for x in albums]
    result = spotify.current_user_saved_albums_add(albums=album_ids)
    print(result)
    for a in albums:
        title = a.get('title')
        artist = a.get('artist')
        key = f'{title} / {artist}'
        if key in apple_music_album_map:
            apple_music_album_map[key]['status'] = 'saved'
    time.sleep(1/30)

_util.write_tsv(apple_music_album_list_path, list(apple_music_album_map.values()))
_util.write_tsv(unknown_album_list_path, [x for x in list(apple_music_album_map.values()) if x.get('status') not in ['saved']])