import csv
import glob
import json
import os
import time

import spotipycharts as sc

def makedirs(dir_path):
    os.makedirs(dir_path, exist_ok=True)

def exists(file_path):
    return os.path.exists(file_path)

def save_file(file_path, text):
    with open(file_path, 'w') as f:
        f.write(text)

def load_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def write_tsv(file_path, data_list, fieldnames=None):
    with open(file_path, 'w') as f:
        if fieldnames is None:
            fieldnames = list(data_list[0].keys())
        writer = csv.DictWriter(f, fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(data_list)

def read_tsv(file_path):
    tsv_file = load_file(file_path)
    return [row for row in csv.DictReader(tsv_file.split('\n'), delimiter='\t')]

def download_charts(charts, chart_type, country_code, freq_type):
    dir_path = f'data/csv/{chart_type.value}-{freq_type.value}-{country_code}'
    makedirs(dir_path)
    duration_list = charts.get_duration_list(chart_type, country_code, freq_type)
    for d in duration_list:
        name = d.get('name').replace('/', '-')
        code = d.get('code')
        file_path = f'{dir_path}/{name}.csv'
        if exists(file_path):
            continue
        charts_csv = charts.download_csv(chart_type, country_code, freq_type, code)
        save_file(file_path, charts_csv)
        print(file_path)
        time.sleep(.1)

def get_chart(chart_type, country_code, freq_type, duration):
    name = duration.get('name').replace('/', '-')
    code = duration.get('code')
    file_path = f'data/csv/{chart_type.value}-{freq_type.value}-{country_code}/{name}.csv'
    charts_csv = load_file(file_path)
    return sc.util.csv_to_list(charts_csv)

def summarize_chart(charts, chart_type, country_code, freq_type):
    duration_list = charts.get_duration_list(chart_type, country_code, freq_type)
    charts_map = {}
    duration_list.reverse()
    for duration in duration_list:
        chart_data = get_chart(chart_type, country_code, freq_type, duration)
        for d in chart_data:
            url = d.get('URL')
            position = int(d.get('Position', '200'))
            streams = int(d.get('Streams', 0))
            if url in charts_map.keys():
                rank = charts_map.get(url)
                rank['Ranked Count'] += 1
                rank['Streams'] += streams
                peak_position = rank.get('Peak Position', 200)
                if peak_position > position:
                    rank['Peak Position'] = position
            else:
                charts_map[url] = {
                    'Track Name': d.get('Track Name'),
                    'Artist': d.get('Artist'),
                    'First Ranked Date': duration.get('name'),
                    'Peak Position': position,
                    'Ranked Count': 1,
                    'Streams': streams,
                    'URL': url,
                }
    return charts_map

def artist_map_to_tsv_data_list(artist_map):
    artist_list = []
    for artist in artist_map.values():
        artist_id = artist.get('id')
        artist_name = artist.get('name')
        followers = artist.get('followers', {})
        followers_total = followers.get('total', 0)
        popularity = artist.get('popularity', 0)
        genres = ' / '.join(artist.get('genres', []))
        artist_list.append({
            'Artist Id': artist_id,
            'Artist Name': artist_name,
            'Followers Total': followers_total,
            'Popularity': popularity,
            'Genres': genres
        })
    return artist_list

def track_map_to_tsv_data(track, artists):
    genres = []
    for a in artists:
            genres.extend(a.get('genres'))
    album = track.get('album', {})
    audio_feature = track.get('audio_feature', {})
    return {
        'Track Name': track.get('name', ''),
        'Track Id': track.get('id' ''),
        'Artist Names': ' / '.join([a.get('name') for a in artists]),
        'Artist Ids': ' / '.join([a.get('id') for a in artists]),
        'Genres': ' / '.join(genres),
        'Duration': track.get('duration_ms', 0),
        'Release Date': album.get('release_date', ''),
        'Popularity': track.get('popularity', 0),
        'Key': audio_feature.get('key', 0),
        'Mode': audio_feature.get('mode', 0),
        'Time Signature': audio_feature.get('time_signature', 0),
        'Tempo': audio_feature.get('tempo', 0),
        'Danceability': audio_feature.get('danceability', 0),
        'Energy': audio_feature.get('energy', 0),
        'Loudness': audio_feature.get('loudness', 0),
        'Speechiness': audio_feature.get('speechiness', 0),
        'Acousticness': audio_feature.get('acousticness', 0),
        'Instrumentalness': audio_feature.get('instrumentalness', 0),
        'Liveness': audio_feature.get('liveness', 0),
        'Valence': audio_feature.get('valence', 0),
    }

def track_map_to_tsv_data_list(track_map, artist_map):
    track_list = []
    for track in track_map.values():
        artists = track.get('artists', [])
        artists_list = []
        for a in artists:
                artist = artist_map.get(a.get('id'))
                if artist is not None:
                    artists_list.append(artist)
        track_list.append(track_map_to_tsv_data(track, artists_list))
    return track_list

def get_tsv_track_data(db, ranking_track):
    track_id = ranking_track.get('URL')
    track_result = db.get_track(track_id)
    artists = track_result.get('artists', [])
    artist_results = []
    for a in artists:
        artist_result = db.get_artist(a.get('id'))
        artist_results.append(artist_result)
    tsv_data = track_map_to_tsv_data(track_result, artist_results)
    del tsv_data['Track Id']
    return tsv_data

def get_genre_map(db):
    artist_map = db.get_artist_map()
    genre_map = db.get_genre_map()

    for d in artist_map.values():
        genres = d.get('genres', [])
        for g in genres:
            if g == '':
                continue
            if g not in genre_map:
                genre_map[g] = {
                    'Genre': g,
                    'Category': '',
                    'Country Name': '',
                    'Country': '',
                    'Area 2': '',
                    'Area 1': ''
                }
    return genre_map

def search_charts(db, charts_data, condition={}):
    genre_list = db.search_genre(**condition)
    print(len(genre_list))

    search_track_list = []
    for d in charts_data:
        track_data = get_tsv_track_data(db, d)
        d.update(track_data)
        genres = d.get('Genres', []).split(' / ')
        for g in genres:
            if g in genre_list:
                genre_info = db.get_genre(g)
                d.update(genre_info)
                search_track_list.append(d)
                break
    print(len(search_track_list))
    return search_track_list

def update_playlist(spotify_client, user_id, playlist_id, track_list_data):
    track_list = [spotify_client._get_id('track', d.get('URL')) for d in track_list_data]

    playlist_tracks = []
    results = spotify_client.playlist_tracks(playlist_id)
    playlist_tracks.extend(results['items'])
    while results['next']:
        results = spotify_client.next(results)
        playlist_tracks.extend(results['items'])

    playlist_track_list = [d.get('track', {}).get('id') for d in playlist_tracks]
    print(len(playlist_track_list))
    add_track_list = [d for d in track_list if d not in playlist_track_list]
    print(len(add_track_list))
    remove_track_list = [d for d in playlist_track_list if d not in track_list]
    print(len(remove_track_list))

    for id in range(0, len(add_track_list), 100):
        spotify_client.user_playlist_add_tracks(user_id, playlist_id, add_track_list[id:id+100])
        time.sleep(.1)


class SpotifyDatabase():
    def __init__(self, spotify_client=None, artist_dir_path=None, track_dir_path=None, genre_file_path=None):
        self._client = spotify_client
        self._artist_dir_path = artist_dir_path
        self._track_dir_path = track_dir_path
        self._genre_file_path = genre_file_path
        self._genre_map = {}
        if self._genre_file_path is not None:
            genre_list = read_tsv(self._genre_file_path)
            for g in genre_list:
                self._genre_map[g.get('Genre')] = g

    def get_artist_map(self):
        if self._artist_dir_path is None:
            return None
        json_list = glob.glob(f'{self._artist_dir_path}/*.json')
        artist_map = {}
        for file_path in json_list:
            artist_json = load_file(file_path)
            artist = json.loads(artist_json)
            artist_map[artist.get('id')] = artist
        return artist_map

    def get_track_map(self):
        if self._track_dir_path is None:
            return None
        json_list = glob.glob(f'{self._track_dir_path}/*.json')
        track_map = {}
        for file_path in json_list:
            track_json = load_file(file_path)
            track = json.loads(track_json)
            track_map[track.get('id')] = track
        return track_map

    def get_genre_map(self):
        return self._genre_map

    def get_track(self, track_id):
        track_id = self._client._get_id('track', track_id)
        if self._track_dir_path is None:
            return None
        track_file_path = f'{self._track_dir_path}/{track_id}.json'
        if exists(track_file_path):
            track_json = load_file(track_file_path)
            return json.loads(track_json)
        elif self._client is not None:
            print(f'get track: {track_id}')
            track_result = self._client.track(track_id)
            audio_result = self._client.audio_features(track_id)
            if len(audio_result) > 0:
                track_result.update({'audio_feature': audio_result[0]})
            save_file(track_file_path, json.dumps(track_result))
            time.sleep(.1)
            return track_result
        return None

    def get_artist(self, artist_id):
        artist_id = self._client._get_id('artist', artist_id)
        if self._artist_dir_path is None:
            return None
        artist_file_path = f'{self._artist_dir_path}/{artist_id}.json'
        if exists(artist_file_path):
            artist_json = load_file(artist_file_path)
            return json.loads(artist_json)
        elif self._client is not None:
            print(f'get artist: {artist_id}')
            artist_result = self._client.artist(artist_id)
            save_file(artist_file_path, json.dumps(artist_result))
            return artist_result
        return None

    def get_genre(self, genre_code):
        return self._genre_map.get(genre_code)

    def update_track_data(self, track_id):
        track_data = self.get_track(track_id)
        if track_data is None:
            return
        artists = track_data.get('artists', [])
        for a in artists:
            self.get_artist(a.get('id'))

    def search_genre(self, country=None, category=None, area1=None, area2=None):
        genre_list = self._genre_map.values()
        if country is not None:
            genre_list = [x for x in genre_list if x.get('Country') == country]
        if category is not None:
            genre_list = [x for x in genre_list if x.get('Category') == category]
        if area1 is not None:
            genre_list = [x for x in genre_list if x.get('Area 1') == area1]
        if area2 is not None:
            genre_list = [x for x in genre_list if x.get('Area 2') == area2]
        return [x.get('Genre') for x in genre_list]
