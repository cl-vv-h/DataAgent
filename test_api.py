from utils.api import get_short_term_data, get_long_term_data, get_market_cap_3y

# get_long_term_data("sh","600310")
import akshare as ak

market = "sh"
ticker = "600315"
try:
    # res = get_long_term_data(market, ticker)
    # print(ak.stock_financial_analysis_indicator_em(symbol="301389.SZ", indicator="按报告期").column.tolist())
    # print(res) 
    print(get_market_cap_3y(ticker))
except Exception as e:
    print(e)
    ev_ebitda = None