data配下にjsonファイル(Spotify APIの取得結果を保存して重複リクエストしないようにしてる)やcsvファイルが大量に吐かれます

# HOW TO INSTALL
```
# pyenvのインストール
# https://qiita.com/koooooo/items/b21d87ffe2b56d0c589b
git clone git://github.com/yyuu/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
source ~/.bash_profile
# python 3.7 のインストール
pyenv install 3.7.2
pyenv local 3.7.2
# pip install
pip install spotipy --upgrade
pip install git+https://github.com/tai-fukaya/spotipycharts --upgrade
# _const.pyのコピー
cp _const.py.template _const.py
# _const.pyの各変数を自分用に書き換える
```

# スクリプト説明
## analyse-spotifycharts.py
指定地域のチャートを全取得して、曲情報一覧を生成します
## update-somewhere-in-somewhere-playlist.py
指定地域のチャートの中の特定地域の楽曲のプレイリストを作成します
## save-database.py
国、トラック、アーティスト、ジャンルのデータのtsvファイル書き出し

# TODO
- [x] 指定地域でのチャートにランクインした楽曲一覧
- [x] 指定地域での出身地で絞った楽曲一覧
    - [x] プレイリストにすでに楽曲がある場合は、追加しない
期間は全て
- [ ] 地域ごとの傾向をしらべる
地域ごとのジャンルの割合の傾向
地域ごとのアーティストの出身地の傾向
地域ごとの楽曲のパラメーターの傾向
- [ ] 指定地域での一定期間で新しく出てきた楽曲一覧
- [ ] 指定地域での一定期間で新しく出てきた楽曲を出身地で絞った一覧
どこの地域で、どの曲が聞かれ始めたのかを見る
- [ ] 指定プレイリストの新しく出てきた楽曲一覧

# 参考になる記事
https://note.com/takashiasayan/n/nff5794ed30fe  
https://qiita.com/kazuya-n/items/fbee07ef778e166cb6dd  
https://qiita.com/yuki_uchida/items/35bc6e3d3d385befe350  
https://qiita.com/hidekoji/items/6b9680798d4d9b03ea9a  
https://note.com/hkrrr_jp/n/n06572cdbbe8c  
