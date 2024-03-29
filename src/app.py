
#%%
import pandas as pd
import streamlit as st
import scraping_jma
from scraping_jma import scraping_jma_daily_data_from_2020_to_latest
import plotly.express as px
import importlib
importlib.reload(scraping_jma)
import base64
# %%

@st.cache_data
def get_data(PREC_NO, BLOCK_NO):
    # 東京のデータ取得
    data_jma = scraping_jma_daily_data_from_2020_to_latest(PREC_NO, BLOCK_NO)
    return data_jma


def download_csv(data):
    # ダウンロードボタンを表示
    # CSV ファイルとしてデータフレームをダウンロード
    csv = data.to_csv(index=False, encoding='utf-8-sig')  # UTF-8 BOM 形式で保存
    b64 = base64.b64encode(csv.encode()).decode()  # CSV を base64 エンコード
    filename = st.text_input("保存時のファイル名を入力してください", "data.csv")  # ユーザーにファイル名を入力してもらう
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

    # データフレームを表示
    st.write(data)

    return None

st.title('気象庁データをスクレイピング')

st.header("観測地の設定")
PREC_NO = st.text_input('PREC NO', placeholder='東京都は44')
BLOCK_NO = st.text_input('BLOCK_NO', placeholder='観測地東京は47662')


st.write("観測地の番号はこちらから")
st.write("http://k-ichikawa.blog.enjoy.jp/etc/HP/htm/jmaP0.html")

if PREC_NO and BLOCK_NO:  # PREC_NOとBLOCK_NOが入力された場合のみ実行
    st.header("スクレイピングデータ")
    # ダウンロードボタンを表示
    data_jma = get_data(PREC_NO, BLOCK_NO)
    download_csv(data_jma)

    st.header("可視化")
    # float型の列だけを抽出
    float_columns = data_jma.select_dtypes(include=['float']).columns
    selected_column = st.selectbox("時系列PLOTする変数を選択してください", options=float_columns)
    # グラフの描画
    fig = px.line(data_jma, x=data_jma.index, y=selected_column, title='時系列PLOT')
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    # プロットをStreamlitで表示
    st.plotly_chart(fig)

