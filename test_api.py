from utils.api import get_short_term_data, get_long_term_data

# get_long_term_data("sh","600310")
import akshare as ak

market = "sh"
ticker = "600310"
try:
    indicator = ak.stock_financial_analysis_indicator(ticker, start_year="2022")
    cf_yearly = ak.stock_cash_flow_sheet_by_yearly_em(market + ticker)
    profit_yearly = ak.stock_profit_sheet_by_yearly_em(market + ticker)
    print(cf_yearly)
    print(profit_yearly)
    ebit = profit_yearly.iloc[0].get('营业利润')
    depr_amort = cf_yearly.iloc[0].get('折旧和摊销') or 0
    ebitda = (ebit or 0) + depr_amort
    market_cap = indicator.iloc[0].get('market_cap')
    balance_yearly = ak.stock_balance_sheet_by_yearly_em(ticker)
    total_debt = balance_yearly.iloc[0].get('负债合计')
    cash = balance_yearly.iloc[0].get('货币资金')
    ev = (market_cap or 0) + (total_debt or 0) - (cash or 0)
    ev_ebitda = ev / ebitda if ebitda and ev else None
except Exception as e:
    print(e)
    ev_ebitda = None