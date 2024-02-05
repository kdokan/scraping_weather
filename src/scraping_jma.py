
#%%
###############
# ライブラリ
###############

import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup

############
# 関数
############

def make_pandasdf_from_html(html_code_data_part_in_url):

    """
    function:
        HTML形式で取得したデータをpandas dataframeに変換する
    args:
        html_code_data_part_in_url: beautifulsoupで取得したデータフレームに変換したいHTML形式のデータ
    return:
        ターゲット月のpandas dataframe形式のデータ
    """

    # データのヘッダーを定義
    HEADER_IN_DATA = [
        "気圧_現地", "気圧_海面", 
        "合計降水量", "最大降水量_1時間内", "最大降水量_10分間内", 
        "平均気温", "最高気温", "最低気温", 
        "平均湿度", "最小湿度", 
        "平均風速", "最大風速", "最大風速時風向", "最大瞬間最大風速", "最大瞬間最大風速時風向", 
        "日照時間", 
        "降雪量", "最深積雪量", 
        "天気概況_昼", "天気概況_夜"]
    # カラム数をもとにfor文を実行することで日付内のデータかを判別する
    NUM_COLUMN = len(HEADER_IN_DATA) 
    # ターゲット月の日数を算出して定義
    DAYS_IN_TARGET_MONTH = int(len(html_code_data_part_in_url)/NUM_COLUMN) 

    # データ格納用の空のデータフレーム作成
    data_in_url = pd.DataFrame(columns = HEADER_IN_DATA)

    # ターゲット月のデータの格納
    for order_rows in range(DAYS_IN_TARGET_MONTH):
        daily_data_in_url = [] # 日毎のデータを格納する用のからリスト作成
        for order_columns in range(NUM_COLUMN):
            daily_data_in_url.append(html_code_data_part_in_url[order_rows * NUM_COLUMN + order_columns].text)
        data_in_url.loc[order_rows] = daily_data_in_url

    return data_in_url


def requests_jma_data_from_url(url):
    """
    function:
        urlのページの気象データ部分をHTML形式で取得
    args:
        欲しい月のurl
    return:
        該当月のHTML形式のデータ
    """
    response_from_requests_url = requests.get(url)
    html_code_in_url = BeautifulSoup(response_from_requests_url.content,"html.parser")
    html_code_data_part_in_url = html_code_in_url.find_all(class_ = "data_0_0") # 気象データの表をdata_0_0をトリガーに探す
    return html_code_data_part_in_url


def scraping_jma_in_target_month(url, year, month):
    """
    function:
        urlのページの気象データ部分をpandas dataframe形式で取得
    args:
        欲しい月のurl
    return:
        該当月のpandas形式のデータ
    """

    html_code_data_part_in_url = requests_jma_data_from_url(url)
    data_in_url = make_pandasdf_from_html(html_code_data_part_in_url)
    # indexを日付データに変換
    data_in_url.index = data_in_url.index+1
    data_in_url.index = str(year) + "-" + str(month) + "-" + data_in_url.index.astype(str)
    data_in_url.index = pd.to_datetime(data_in_url.index)

    return data_in_url



def modify_spelling(data):

    """
    function:
        表記揺れやDBにするための整形を施す
    args:
        jmaから抽出してきたdata
    return:
        DBに入れられるようなdataframe
    """

    # 全体に関わる表記揺れ修正 (2019.12.3や9でみられる)
    data = data.replace("\s*\)","",regex=True)
    data = data.replace("\s*\]","",regex=True)

    # 降水量の整形
    ## データがないところは天気が雨ではない日なので降水量0とする
    data.loc[data["合計降水量"] == "--", "合計降水量"] = 0.0
    data.loc[data["最大降水量_1時間内"] == "--", "最大降水量_1時間内"] = 0.0
    data.loc[data["最大降水量_10分間内"] == "--", "最大降水量_10分間内"] = 0.0
    data.loc[data["降雪量"] == "--", "降雪量"] = 0.0
    data.loc[data["最深積雪量"] == "--", "最深積雪量"] = 0.0

    # 日照時間の整形
    data.loc[data["日照時間"] == "×", "日照時間"] = 0.0

    # データ型の辞書
    modify_dtypes = {
        "気圧_現地": float,
        "気圧_海面": float,
        "合計降水量": float,
        "最大降水量_1時間内": float,
        "最大降水量_10分間内": float,
        "平均気温": float,
        "最高気温": float,
        "平均湿度": float,
        "最小湿度": float,
        "平均風速": float,
        "最大風速": float,
        "最大風速時風向": str,
        "最大瞬間最大風速": float,
        "最大瞬間最大風速時風向": str,
        "日照時間": float,
        "降雪量": float,
        "最深積雪量": float,
        "天気概況_昼": str,
        "天気概況_夜": str
    }


    data = data.astype(modify_dtypes)

    return data

def scraping_jma_daily_data_from_2016_to_latest(PREC_NO, BLOCK_NO):
    # 今日の日付を取得する
    today = datetime.now()
    today_date = today.date()

    # 2016年から最新月のデータまで取得する
    data_jma = pd.DataFrame()

    for year in range(2016, today_date.year): # 2016年以降のデータを取得
        for month in range(1, 13): # 1~12月でループ
            url = f"https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php?prec_no={PREC_NO}&block_no={BLOCK_NO}&year={year}&month={month}&day=1&view="
            data_jma = pd.concat([data_jma, scraping_jma_in_target_month(url, year, month)])

    year = today_date.year
    for month in range(1, today_date.month+1):
        url = f"https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php?prec_no=44&block_no=47662&year={year}&month={month}&day=1&view="
        data_jma = pd.concat([data_jma, scraping_jma_in_target_month(url, year, month)])

    # ないデータは不要なので
    data_jma = data_jma[data_jma.index < today_date.strftime("%Y-%-m-%-d")]

    # 表記揺れやデータ型など整頓
    data_jma = modify_spelling(data_jma)

    return data_jma


#%%

##########
# 実行
##########

# 東京都 東京のCODE
PREC_NO = 44
BLOCK_NO = 47662

# 東京のデータ取得
data_jma = scraping_jma_daily_data_from_2016_to_latest(PREC_NO, BLOCK_NO)


#%%
data = data_jma
data


# %%
import matplotlib.pyplot as plt
plt.plot(data.index, data["平均気温"])


# %%
