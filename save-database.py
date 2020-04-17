import spotipycharts as sc

import _util

charts = sc.Spotipycharts()
country_list = charts.get_country_list()

print(f'country: {len(country_list)}')
_util.write_tsv('data/country-data.tsv', country_list)

track_data_path = 'data/track'
artist_data_path = 'data/artist'
genre_data_path = 'data/genre-data.tsv'

db = _util.SpotifyDatabase(
    track_dir_path=track_data_path,
    artist_dir_path=artist_data_path,
    genre_file_path=genre_data_path
)

artist_map = db.get_artist_map()
track_map = db.get_track_map()

artist_list = _util.artist_map_to_tsv_data_list(artist_map)
print(f'artist: {len(artist_list)}')
_util.write_tsv('data/artist-data.tsv', artist_list)
track_list = _util.track_map_to_tsv_data_list(track_map, artist_map)
print(f'track: {len(track_list)}')
_util.write_tsv('data/track-data.tsv', track_list)
genre_map = _util.get_genre_map(db)
print(f"genre: {len(genre_map.keys())}")
_util.write_tsv(genre_data_path, list(genre_map.values()))
