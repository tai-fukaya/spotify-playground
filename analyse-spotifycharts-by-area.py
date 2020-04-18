import datetime

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
freq_type = sc.FrequencyType.DAILY

track_data_path = 'data/track'
artist_data_path = 'data/artist'
genre_data_path = 'data/genre-data.tsv'

begin_date = datetime.datetime(2020, 4, 4)
end_date = datetime.datetime(2020, 4, 10)

dir_path = f'data/{begin_date.strftime("%m-%d-%Y")}--{end_date.strftime("%m-%d-%Y")}'
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
    _util.download_charts(
        charts, chart_type, country_code, freq_type,
        begin_date=begin_date, end_date=end_date
    )
    charts_map = _util.summarize_chart(
        charts, chart_type, country_code, freq_type,
        begin_date=begin_date, end_date=end_date
    )
    print(f"{country_code}: {len(charts_map.values())} tracks")
    charts_data = list(charts_map.values())
    for i, d in enumerate(charts_data):
        database.update_track_data(d.get('URL'))
        d.update(_util.get_tsv_track_data(database, d))
    _util.write_tsv(charts_file_path, charts_data)

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

# ダウンロードとサマリー生成
for c in country_list:
    code = c.get('code')
    summarize_charts_by_area(code)

# 地域ごとの楽曲の傾向

# 地域ごとのジャンルと、出身地の傾向
