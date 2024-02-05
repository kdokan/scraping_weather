

#%%
###############
# ライブラリ
###############


import importlib
import scraping_jma
from scraping_jma import scraping_jma_daily_data_from_2016_to_latest
importlib.reload(scraping_jma)


#%%

###########
# 実行
###########

# 東京都 東京のCODE
PREC_NO = 44
BLOCK_NO = 47662

# 東京のデータ取得
data_jma = scraping_jma_daily_data_from_2016_to_latest(PREC_NO, BLOCK_NO)


#%%

############
# お試しの可視化
############

import matplotlib.pyplot as plt
plt.plot(data_jma.index, data_jma["平均気温"])



