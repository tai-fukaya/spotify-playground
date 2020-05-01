import re

import requests
from bs4 import BeautifulSoup

import _util

genre_data_path = 'data/genre-data.tsv'

db = _util.SpotifyDatabase(
    genre_file_path=genre_data_path
)
genre_map = db.get_genre_map()

print(len(genre_map.values()))

r = requests.get('http://everynoise.com/everynoise1d.cgi?scope=all')
soup = BeautifulSoup(r.text, 'lxml')

selector = soup.find_all('tr')
print(len(selector))

def get_genre_category(genre):
    genre_map = {
        'traditional': 'traditional',
        'worship': 'traditional',
        'tradicional': 'traditional',
        'folk': 'traditional',
        'blues': 'traditional',
        'roots': 'traditional',
        'indie': 'indie',
        'slow core': 'indie',
        'rock': 'rock',
        'pop': 'pop',
        'idol': 'pop',
        'singer-songwriter': 'pop',
        'hip hop': 'hip hop',
        'trap': 'hip hop',
        'rap': 'hip hop',
        'reggae': 'hip hop',
        'r&b': 'r&b',
        'soul': 'r&b',
        'jazz': 'jazz',
        'punk': 'rock',
        'emo': 'rock',
        'metal': 'metal',
        'hardcore': 'metal',
        'core': 'metal',
        'classic': 'classic',
        'electronic': 'electronic',
        'idm': 'electronic',
        'house': 'electronic',
        'techno': 'electronic',
        'dance': 'dance',
        'edm': 'dance',
        'trance': 'dance',
        'beat': 'dance',
        'funk': 'dance',
        'experimental': 'experimental',
        'ambient': 'experimental',
    }
    for k, v in genre_map.items():
        if k in genre:
            return v
    return ''

for s in selector:
    genre = s.find_all('td', attrs={'class': 'note'})[1].text
    if genre not in genre_map:
        genre_map[genre] = {
            'Genre': genre,
            'Category': '',
            'Country Name': '',
            'Country': '',
            'Area 2': '',
            'Area 1': ''
        }
    genre_data = genre_map[genre]
    # genre_data['Category'] = get_genre_category(genre)
    category = genre_data.get('Category')
    if category == '':
        genre_data['Category'] = get_genre_category(genre)

print(len(genre_map.values()))
_util.write_tsv(genre_data_path, list(genre_map.values()))
