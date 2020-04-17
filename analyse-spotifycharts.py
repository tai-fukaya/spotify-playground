import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipycharts as sc

import _const
import _util

"""
Spotifycharts.com から、指定した地域のチャート情報を全部取得し、
曲ごとに、何回チャートにランクインしたか、最高順位、再生回数を取得します。
チャートについては、TOP200と、VIRALの２種類があります。
"""

chart_type = sc.ChartType.VIRAL
freq_type = sc.FrequencyType.DAILY
country_code = 'global'

charts_file_path = f'data/tsv/analyse-charts-{chart_type.value}-{freq_type.value}-{country_code}.tsv'
track_data_path = 'data/track'
artist_data_path = 'data/artist'

charts = sc.Spotipycharts()

# data/tsv フォルダを作る
_util.makedirs('data/tsv')

# チャート情報(csv)をダウンロードします。
print("start: download csv")
_util.download_charts(charts, chart_type, country_code, freq_type)

# 曲ごとの情報にまとめます。
print("start: summary spotifycharts")
charts_map = _util.summarize_chart(charts, chart_type, country_code, freq_type)
print(f"{len(charts_map.values())} tracks")
# いったん、ファイル保存する
_util.write_tsv(charts_file_path, list(charts_map.values()))

# 曲ごとにSpotify APIのトラックデータを取得します。
print("start: get track data")
charts_data = _util.read_tsv(charts_file_path)

client_id = _const.CLIENT_ID
client_secret = _const.CLIENT_SECRET
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(client_id, client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

database = _util.SpotifyDatabase(
    spotify_client=spotify,
    track_dir_path=track_data_path,
    artist_dir_path=artist_data_path
)

for i, d in enumerate(charts_data):
    print(f'track {i}')
    database.update_track_data(d.get('URL'))
    d.update(_util.get_tsv_track_data(database, d))

# トラック情報を付与してファイルを保存します。
print("start: save file")
_util.write_tsv(charts_file_path, charts_data)
print("success: analyse spotifycharts")