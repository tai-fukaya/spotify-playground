import spotipy
import spotipy.util as util

from spotipy.oauth2 import SpotifyClientCredentials
import spotipycharts as sc

import _const
import _util

"""
Spotifycharts.com から、指定した地域のチャート情報を全部取得し、
曲ごとに、何回チャートにランクインしたか、最高順位、再生回数を取得します。
チャートについては、TOP200と、VIRALの２種類があります。
その上で、トラックに参加しているアーティスト情報から、どこの国の歌かを特定し、
該当エリアの楽曲をプレイリストに追加します。

※ プレイリストについては、あらかじめ作成し、プレイリストのSpotify URIを取得する必要があります。
※ ジャンルデータについては、手動でどこの国かを設定する必要があるので、生成されたdata/genre-data.tsvを編集後、再度このスクリプトを実行してください。
"""

chart_type = sc.ChartType.VIRAL
freq_type = sc.FrequencyType.DAILY
country_code = 'global'


search_condition_list = [{
    'condition': {'area1': 'Asia'},
    'playlist_id': 'spotify:playlist:543hyxdAZrBH2su7bp6E84'
}, {
    'condition': {'area1': 'Africa'},
    'playlist_id': 'spotify:playlist:7jjLPsFnsvLKk8vYwm9ZsY'
}, {
    'condition': {'area1': 'Middle Eastern'},
    'playlist_id': 'spotify:playlist:2Tp8LRZvpG9t7jEcjFXfMn'
}]

charts_file_path = f'data/tsv/analyse-charts-{chart_type.value}-{freq_type.value}-{country_code}.tsv'
track_data_path = 'data/track'
artist_data_path = 'data/artist'
genre_data_path = 'data/genre-data.tsv'
search_track_list_path = f'data/tsv/<somewhere>-in-{chart_type.value}-{freq_type.value}-{country_code}.tsv'

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

user_id = _const.USER_ID
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

for i, d in enumerate(charts_data):
    print(f'track {i}')
    database.update_track_data(d.get('URL'))
    d.update(_util.get_tsv_track_data(database, d))

# トラック情報を付与してファイルを保存します。
print("start: save analyse file")
_util.write_tsv(charts_file_path, charts_data)

# ジャンルデータを生成します。
print("start: update genre data")
genre_map = _util.get_genre_map(database)
print(f"{len(genre_map.keys())} genres")
_util.write_tsv(genre_data_path, list(genre_map.values()))

# 手動でどこの国かを設定する必要があるので、生成されたdata/genre-data.tsvを編集後、再度このスクリプトを実行してください。

# Spotify Dashboard で、Redirect URIに、"http://127.0.0.1:8080/" を設定しておく。
# 参考URL:
# http://sakanaaas.hateblo.jp/entry/2017/07/02/122740
token = util.prompt_for_user_token(
    user_id,
    scope='playlist-modify-public',
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://127.0.0.1:8080/')
spotify._auth = token
for config in search_condition_list:
    condition = config.get('condition', {})
    playlist_id = config.get('playlist_id')
    # 特定地域のトラックデータを抽出します。
    print(f'search charts {condition}')
    track_list_data = _util.search_charts(database, charts_data, condition)
    condition_values = '-'.join(condition.values())
    track_list_path = search_track_list_path.replace('<somewhere>', condition_values.lower().replace(" ", "-"))
    _util.write_tsv(track_list_path, track_list_data)
    # プレイリストを更新します。
    print(f'update playlist {playlist_id}')
    _util.update_playlist(spotify, user_id, playlist_id, track_list_data)
