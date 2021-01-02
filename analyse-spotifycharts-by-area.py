import datetime
import json
import statistics

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipycharts as sc

import _const
import _util

"""
Spotifycharts.com から、指定した期間の指定した地域のチャート情報を取得し、
地域ごとに、曲の傾向と、ジャンルの傾向を調べます。
"""

chart_type = sc.ChartType.VIRAL
freq_type = sc.FrequencyType.WEEKLY

track_data_path = 'data/track'
artist_data_path = 'data/artist'
genre_data_path = 'data/genre-data.tsv'

begin_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2020, 12, 31)

duration = f'{begin_date.strftime("%m-%d-%Y")}--{end_date.strftime("%m-%d-%Y")}'
dir_path = f'data/{duration}'
_util.makedirs(dir_path)

charts = sc.Spotipycharts()

client_id = _const.CLIENT_ID
client_secret = _const.CLIENT_SECRET
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

database = _util.SpotifyDatabase(
    spotify_client=spotify,
    track_dir_path=track_data_path,
    artist_dir_path=artist_data_path,
    genre_file_path=genre_data_path
)

def summarize_charts_by_area(country_code):
    charts_file_path = f'{dir_path}/analyse-charts-{chart_type.value}-{freq_type.value}-{country_code}.tsv'
    print(f'{country_code}: start download')
    _util.download_charts(
        charts, chart_type, country_code, freq_type,
        begin_date=begin_date, end_date=end_date
    )
    print(f'{country_code}: start summarize')
    charts_map = _util.summarize_chart(
        charts, chart_type, country_code, freq_type,
        begin_date=begin_date, end_date=end_date
    )
    print(f"{country_code}: {len(charts_map.values())} tracks")
    charts_data = list(charts_map.values())
    for i, d in enumerate(charts_data):
        database.update_track_data(d.get('URL'))
        d.update(_util.get_tsv_track_data(database, d))
        # ジャンルごとのカテゴリ、国、エリアをつめる
        genres = d.get('Genres', '').split(' / ')
        categories = []
        countries = []
        area2_list = []
        area1_list = []
        for g in genres:
            genre = database.get_genre(g)
            if genre is None:
                continue
            category = genre.get('Category')
            country = genre.get('Country')
            area2 = genre.get('Area 2')
            area1 = genre.get('Area 1')
            if category is not None and category != '':
                categories.append(category)
            if country is not None and country != '':
                countries.append(country)
            if area2 is not None and area2 != '':
                area2_list.append(area2)
            if area1 is not None and area1 != '':
                area1_list.append(area1)
        categories = list(set(categories))
        countries = list(set(countries))
        area2_list = list(set(area2_list))
        area1_list = list(set(area1_list))
        d['Categories'] = ' / '.join(categories)
        d['Countries'] = ' / '.join(countries)
        d['Area2'] = ' / '.join(area2_list)
        d['Area1'] = ' / '.join(area1_list)
    _util.write_tsv(charts_file_path, charts_data)
    return charts_data

country_list = [
    {'name': 'Global', 'code': 'global'},
    {'name': 'United States', 'code': 'us'},
    {'name': 'United Kingdom', 'code': 'gb'},
    {'name': 'Australia', 'code': 'au'},
    {'name': 'Brazil', 'code': 'br'},
    {'name': 'Spain', 'code': 'es'},
    {'name': 'France', 'code': 'fr'},
    {'name': 'Mexico', 'code': 'mx'},
    {'name': 'Poland', 'code': 'pl'},
    {'name': 'Sweden', 'code': 'se'},
    {'name': 'Turkey', 'code': 'tr'},
    {'name': 'South Africa', 'code': 'za'},
    {'name': 'Hong Kong', 'code': 'hk'},
    {'name': 'Indonesia', 'code': 'id'},
    {'name': 'India', 'code': 'in'},
    {'name': 'Japan', 'code': 'jp'},
    {'name': 'Malaysia', 'code': 'my'},
    {'name': 'Philippines', 'code': 'ph'},
    {'name': 'Singapore', 'code': 'sg'},
    {'name': 'Thailand', 'code': 'th'},
    {'name': 'Taiwan', 'code': 'tw'},
    {'name': 'Viet Nam', 'code': 'vn'}
]
# country_list = charts.get_country_list()

analyse_results = []
master_country_list = []
# ダウンロードとサマリー生成
for c in country_list:
    code = c.get('code')
    # 楽曲の特徴の傾向
    audio_features = {
        'Duration': [],
        'Key': [],
        'Mode': [],
        'Time Signature': [],
        'Tempo': [],
        'Danceability': [],
        'Energy': [],
        'Loudness': [],
        'Speechiness': [],
        'Acousticness': [],
        'Instrumentalness': [],
        'Liveness': [],
        'Valence': []
    }
    category_map = {}
    country_map = {}
    area2_map = {}
    area1_map = {}

    charts_data = summarize_charts_by_area(code)
    for d in charts_data:
        count = d.get('Ranked Count')
        audio_features['Duration'].extend([d.get('Duration')]*count)
        audio_features['Key'].extend([d.get('Key')]*count)
        audio_features['Mode'].extend([d.get('Mode')]*count)
        audio_features['Time Signature'].extend([d.get('Time Signature')]*count)
        audio_features['Tempo'].extend([d.get('Tempo')]*count)
        audio_features['Danceability'].extend([d.get('Danceability')]*count)
        audio_features['Energy'].extend([d.get('Energy')]*count)
        audio_features['Loudness'].extend([d.get('Loudness')]*count)
        audio_features['Speechiness'].extend([d.get('Speechiness')]*count)
        audio_features['Acousticness'].extend([d.get('Acousticness')]*count)
        audio_features['Instrumentalness'].extend([d.get('Instrumentalness')]*count)
        audio_features['Liveness'].extend([d.get('Liveness')]*count)
        audio_features['Valence'].extend([d.get('Valence')]*count)

        categories = d.get('Categories', '').split(' / ')
        countries = d.get('Countries', '').split(' / ')
        area2_list = d.get('Area2', '').split(' / ')
        area1_list = d.get('Area1', '').split(' / ')
        for c in categories:
            if c == '':
                c = 'unknown'
            if category_map.get(c) is None:
                category_map[c] = 1
            else:
                category_map[c] += 1
        for c in countries:
            if c == '':
                c = 'unknown'
            if country_map.get(c) is None:
                country_map[c] = 1
            else:
                country_map[c] += 1
        for a in area2_list:
            if a == '':
                a = 'unknown'
            if area2_map.get(a) is None:
                area2_map[a] = 1
            else:
                area2_map[a] += 1
        for a in area1_list:
            if a == '':
                a = 'unknown'
            if area1_map.get(a) is None:
                area1_map[a] = 1
            else:
                area1_map[a] += 1

    master_country_list.extend(country_map.keys())
    analyse_results.append({
        'chart_type': chart_type.value,
        'freq_type': freq_type.value,
        'country_code': code,
        'duration_code': duration,
        'audio_features': {
            'duration': {
                'median': statistics.median(audio_features['Duration']),
                'stdev': statistics.stdev(audio_features['Duration']),
            },
            'key': {
                'median': statistics.median(audio_features['Key']),
                'stdev': statistics.stdev(audio_features['Key']),
            },
            'mode': {
                'median': statistics.median(audio_features['Mode']),
                'stdev': statistics.stdev(audio_features['Mode']),
            },
            'time_signature': {
                'median': statistics.median(audio_features['Time Signature']),
                'stdev': statistics.stdev(audio_features['Time Signature']),
            },
            'tempo': {
                'median': statistics.median(audio_features['Tempo']),
                'stdev': statistics.stdev(audio_features['Tempo']),
            },
            'danceability': {
                'median': statistics.median(audio_features['Danceability']),
                'stdev': statistics.stdev(audio_features['Danceability']),
            },
            'energy': {
                'median': statistics.median(audio_features['Energy']),
                'stdev': statistics.stdev(audio_features['Energy']),
            },
            'loudness': {
                'median': statistics.median(audio_features['Loudness']),
                'stdev': statistics.stdev(audio_features['Loudness']),
            },
            'speechiness': {
                'median': statistics.median(audio_features['Speechiness']),
                'stdev': statistics.stdev(audio_features['Speechiness']),
            },
            'acousticness': {
                'median': statistics.median(audio_features['Acousticness']),
                'stdev': statistics.stdev(audio_features['Acousticness']),
            },
            'instrumentalness': {
                'median': statistics.median(audio_features['Instrumentalness']),
                'stdev': statistics.stdev(audio_features['Instrumentalness']),
            },
            'liveness': {
                'median': statistics.median(audio_features['Liveness']),
                'stdev': statistics.stdev(audio_features['Liveness']),
            },
            'valence': {
                'median': statistics.median(audio_features['Valence']),
                'stdev': statistics.stdev(audio_features['Valence']),
            },
        },
        'category_count': category_map,
        'country_count': country_map,
        'area2_count': area2_map,
        'area1_count': area1_map
    })

# print(json.dumps(analyse_results, indent=4))
_util.save_file(f'{dir_path}/result.json', json.dumps(analyse_results))

master_country_list = list(set(master_country_list))
master_country_list.sort()
tsv_results = []
for r in analyse_results:
    result = {
        'chart_type': r.get('chart_type'),
        'freq_type': r.get('freq_type'),
        'country_code': r.get('country_code'),
        'duration_code': r.get('duration_code'),
        'duration': r.get('audio_features').get('duration').get('median'),
        'key': r.get('audio_features').get('key').get('median'),
        'mode': r.get('audio_features').get('mode').get('median'),
        'time_signature': r.get('audio_features').get('time_signature').get('median'),
        'tempo': r.get('audio_features').get('tempo').get('median'),
        'danceability': r.get('audio_features').get('danceability').get('median'),
        'energy': r.get('audio_features').get('energy').get('median'),
        'loudness': r.get('audio_features').get('loudness').get('median'),
        'speechiness': r.get('audio_features').get('speechiness').get('median'),
        'acousticness': r.get('audio_features').get('acousticness').get('median'),
        'instrumentalness': r.get('audio_features').get('instrumentalness').get('median'),
        'liveness': r.get('audio_features').get('liveness').get('median'),
        'valence': r.get('audio_features').get('valence').get('median'),
    }
    country_count = r.get('country_count', {})
    for c in master_country_list:
        result[c] = country_count.get(c, 0)
    tsv_results.append(result)

_util.write_tsv(f'{dir_path}/result.tsv', tsv_results)
