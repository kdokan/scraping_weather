# ベースイメージの指定
FROM python:3.10

# システムパッケージのアップデート
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    git \
    curl \
    fonts-ipaexfont \
    fonts-noto-cjk \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# pythonライブラリ
COPY requirements.txt .
RUN pip3 install --upgrade pip 
RUN pip3 install --no-cache-dir -r requirements.txt

# matplotlibの設定ファイルのコピー
COPY matplotlibrc /root/.config/matplotlib/matplotlibrc

# 作業ディレクトリ
WORKDIR /home/work/

