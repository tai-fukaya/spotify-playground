import time

import spotipy
import spotipy.util
from spotipy.oauth2 import SpotifyClientCredentials

import _const
import _util

"""
自分が保存しているアルバム一覧と、ジャンル一覧を生成します。
user-library-read
"""
user_id = _const.USER_ID
client_id = _const.CLIENT_ID
client_secret = _const.CLIENT_SECRET

token = spotipy.util.prompt_for_user_token(
    user_id,
    scope='user-library-read',
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://127.0.0.1:8080/')
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(auth=token, client_credentials_manager=client_credentials_manager)

track_data_path = 'data/track'
artist_data_path = 'data/artist'
genre_data_path = 'data/genre-data.tsv'

database = _util.SpotifyDatabase(
    spotify_client=spotify,
    track_dir_path=track_data_path,
    artist_dir_path=artist_data_path,
    genre_file_path=genre_data_path
)

album_list = []
result = spotify.current_user_saved_albums(limit=50)
album_list.extend(result.get('items', []))

while result['next']:
    print(f'get result: {result["next"]}')
    result = spotify.next(result)
    album_list.extend(result.get('items', []))
    time.sleep(1/30)

print(len(album_list))
output_album_list = []
genre_map = {}
for a in album_list:
    album = a.get('album', {})
    artists = album.get('artists', [])
    genres = album.get('genres', [])
    for x in artists:
        artist_result = database.get_artist(x.get('id'))
        genres.extend(artist_result.get('genres', []))
    genres = list(set(genres))
    # genre ごとの統計
    for g in genres:
        if g in genre_map:
            genre_map[g]['Count'] += 1
        else:
            genre_data = database.get_genre(g)
            if genre_data is None:
                genre_data = {
                    'Genre': g,
                    'Category': '',
                    'Country Name': '',
                    'Country': '',
                    'Area 2': '',
                    'Area 1': ''
                }
            genre_data['Count'] = 1
            genre_map[g] = genre_data
    # TODO 全てのtrack情報の取得
    # TODO trackに紐づく、audio_featureの取得
    output_album_list.append({
        'album_type': album.get('album_type'),
        'name': album.get('name'),
        'artist_names': ' / '.join([x.get('name') for x in artists]),
        'label': album.get('label'),
        'release_year': album.get('release_date', '')[:4],
        'release_date': album.get('release_date'),
        'release_date_precision': album.get('release_date_precision'),
        'artist_ids': ' / '.join([x.get('id') for x in artists]),
        'id': album.get('id'),
        'total_tracks': album.get('total_tracks'),
        'result_total_tracks': len(album.get('tracks', {}).get('items', [])),
        'added_at': a.get('added_at'),
        'genres': ' / '.join(genres),
        'popularity': album.get('popularity'),
    })

_util.write_tsv('data/saved/my_albums.tsv', output_album_list)
_util.write_tsv('data/saved/genre.tsv', list(genre_map.values()))

# added_at, album_type, artist_names, artist_ids, genres, id, label,
# name, popularity, release_date, release_date_precision, total_tracks, result_total_tracks
# track_id -> audio_feature, track
