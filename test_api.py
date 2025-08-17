from utils.api import get_short_term_data, get_long_term_data, get_market_cap_3y, get_financial_metrics, get_market_data

# get_long_term_data("sh","600310")
import akshare as ak
from datetime import datetime

market = "sh"
ticker = "600310"
# try:
#     # res = get_long_term_data(market, ticker)
#     # res = get_market_data(ticker)
#     # print(res) 

#     df = ak.stock_zh_a_gdhs_detail_em(ticker)

#     market_cap = df.iloc[0].get("总市值")
#     # 获取最近交易日数据（防止周末或节假日无数据）
#     # 今天日期
#     today = datetime.today()
#     # 去年今日
#     last_year_today = today.replace(year=today.year - 1)
#     # 转换为 YYMMDD 格式
#     today_str = today.strftime("%Y%m%d")
#     last_year_today_str = last_year_today.strftime("%Y%m%d")
#     hist_df = ak.stock_zh_a_daily(symbol=market+ticker,start_date=last_year_today_str, end_date=today_str, adjust="qfq")
# except Exception as e:
#     print(e)
#     ev_ebitda = None
tmp = ak.stock_a_indicator_lg(symbol=ticker)
print(tmp)