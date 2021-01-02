import time

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import _const
import _util

"""
Apple Musicで保存したアルバムを、Spotifyでも保存するようにします。
XCodeから生成したtsvファイルを元に、Spotifyを検索します。
・タイトル、アーティスト名が合致したものは、found.tsvに、
・アーティスト名が合致しなかったものは、unmatched.tsvに、
・どちらも存在しなかったものは、unknown.tsvに保存されます。
"""

apple_music_albums_path = 'data/apple-music/apple-music.tsv'

found_albums_path = 'data/apple-music/found.tsv'
unmatched_artists_path = 'data/apple-music/unmatched.tsv'
unknown_albums_path = 'data/apple-music/unknown.tsv'

# ファイルの読み込み
print('start: read apple music albums data')
album_list = _util.read_tsv(apple_music_albums_path)

found_album_list = []
unmatch_artist_list = []
unknown_album_list = []

client_id = _const.CLIENT_ID
client_secret = _const.CLIENT_SECRET
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

for i, album in enumerate(album_list):
    title = album.get('title')
    artist = album.get('artist')
    if not title:
        continue
    if album.get('status') in ['found', 'saved']:
        continue
    elif 'status' not in album:
        album['status'] = 'unknown'
    result = spotify.search(f"{title} {artist}", limit=30, type='album', market='JP')
    total = result.get('albums', {}).get('total')
    print(f"{i}: {title} / {artist} ({total})")
    if total == 0:
        result = spotify.search(title, limit=30, type='album', market='JP')
        total = result.get('albums', {}).get('total')
        print(f"{i}: {title} / {artist} ({total})")
    albums = result.get('albums', {}).get('items', [])

    is_found = False
    albums_by_unknown = []
    unknown = []
    for a in albums:
        artists = [x.get('name').lower() for x in a.get('artists', [])]
        spotify_album_title = a.get('name')
        album_item = {
            'title': title,
            'artist': artist,
            'id': a.get('id'),
            'album_type': a.get('album_type'),
            'spotify_title': spotify_album_title,
            'spotify_artist': ' / '.join(artists),
            'release_date': a.get('release_date'),
            'uri': a.get('uri')
        }
        if title.lower() == spotify_album_title.lower():
            # TODO アーティストが複数ある場合、AppleMusic側のartistを&で分割する必要がある。
            if artist.lower() in artists:
                found_album_list.append(album_item)
                is_found = True
                break
            else:
                albums_by_unknown.append(album_item)
        else:
            unknown.append(album_item)

    if not is_found:
        if len(albums_by_unknown) > 0:
            unmatch_artist_list.extend(albums_by_unknown)
            album['status'] = 'unmatched'
            print('unmatched')
        else:
            unknown_album_list.extend(unknown)
            album['status'] = 'unknown'
            print('unknown')
    else:
        album['status'] = 'found'
        print('found')
    time.sleep(1/30)

print(len(found_album_list))
print(len(unmatch_artist_list))
print(len(unknown_album_list))

if len(found_album_list):
    _util.write_tsv(found_albums_path, found_album_list)
if len(unmatch_artist_list):
    _util.write_tsv(unmatched_artists_path, unmatch_artist_list)
if len(unknown_album_list):
    _util.write_tsv(unknown_albums_path, unknown_album_list)
_util.write_tsv(apple_music_albums_path, album_list)