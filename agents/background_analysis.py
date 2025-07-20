from langchain.prompts import PromptTemplate
from langchain.tools import Tool

import akshare as ak
import pandas as pd
import pandas_ta as ta

from datetime import datetime, timedelta
import sys
import os
current = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(current)
sys.path.insert(0, parent)
from model import doubao_llm, ds_llm, get_chat_completion

from dotenv import load_dotenv
load_dotenv(override=True)

from utils.logging_config import setup_logger
logger = setup_logger('market_data_agent')

# 1. 获取财务数据（最近5期）
def get_financials(ticker: str) -> pd.DataFrame:
    logger.info("正在获取财务数据...")
    df = ak.stock_financial_analysis_indicator(ticker)

    logger.info(f"已获取财务数据，数据条目为{str(df.shape)}")
    return df.tail(5)

# 2. 获取估值数据：PE、市净率等
def get_valuation(ticker: str) -> pd.DataFrame:
    logger.info("正在获取估值数据...")
    df = ak.stock_a_indicator_lg(symbol=ticker)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.set_index('trade_date').sort_index()

    # 计算 5 年前的时间边界
    end = df.index.max()
    start = end - pd.DateOffset(years=5)

    # 筛选近 5 年
    df_5y = df.loc[start:end]

    # 按月取最后一条记录
    df_monthly = df_5y.resample('ME').last().dropna(subset=['pe', 'pe_ttm', 'pb'])

    logger.info(f"已获取估值数据，数据条目为{str(df_monthly.shape)}")

    return df_monthly[['pe', 'pe_ttm', 'pb']]

# 3. 获取行情 & 计算技术指标
def get_ohlcv_and_tech(ticker: str) -> pd.DataFrame:
    logger.info("正在获取指标数据...")
    # 计算日期范围
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    sd = start_date.strftime("%Y%m%d")
    ed = end_date.strftime("%Y%m%d")
    
    # 获取数据，仅取最近一年的历史
    df = ak.stock_zh_a_hist(symbol=ticker, period="daily", start_date=sd, end_date=ed, adjust="qfq")
    
    # 重命名与索引设置
    df = (
        df.rename(columns={
            '日期':'date', '成交量':'volume',
            '开盘':'open','收盘':'close',
            '最高':'high','最低':'low'
        })
        .set_index('date')
        .astype(float)
    )
    
    # 计算技术指标
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma60'] = df['close'].rolling(60).mean()
    macd = ta.macd(df['close'])
    df['macd'], df['macd_signal'], df['macd_hist'] = (
        macd['MACD_12_26_9'], macd['MACDs_12_26_9'], macd['MACDh_12_26_9']
    )
    df['rsi14'] = ta.rsi(df['close'], length=14)
    df['turnover'] = df['volume'] / df['volume'].mean()
    
    logger.info(f"已获取指标数据，数据条目为{str(df.shape)}")
    return df

# 4. 获取调研信息
def fetch_insights(ticker: str) -> str:
    logger.info("正在获取市场调研数据...")
    from langchain_tavily import TavilySearch
    tav = TavilySearch(max_results=3, topic="general")
    res = tav.run(tool_input=f"{ticker} 调研报告 业务 业绩 营收")
    content = "\n".join(r["content"] for r in res["results"][:5])
    logger.info(f"已获取市场调研数据，长度为{len(content)}")
    return content

# 注册工具
finance_tool = Tool("get_financials", func=get_financials, description="获取最近5期财务数据")
val_tool = Tool("get_valuation", func=get_valuation, description="获取估值指标 PE/PB")
tech_tool = Tool("get_ohlcv_and_tech", func=get_ohlcv_and_tech, description="获取行情并计算技术指标")
insight_tool = Tool("fetch_insights", func=fetch_insights, description="获取机构调研信息")

# Prompt
template = """
你是一个资深的金融、财务领域专家，现在政府机关请你调查以下这家公司
公司代码: {ticker}

【一】基本情况与生意特征（根据财务最近5期）：
{financials}

【二】核心逻辑 & 业务分析：
请结合上述数据，分析“市场空间、竞争格局、成长驱动、公司优势”。

【三】估值计算（PE、PB 等）：
{valuation}

【四】技术面 & 近期走势（最新值）：
{tech_summary}

【五】机构调研亮点：
{insights}

请整合输出分析结论。
"""

# 节点主函数
def analyze_company_node(ticker: str):
    fin = finance_tool.func(ticker)
    val = val_tool.func(ticker)
    df = tech_tool.func(ticker)
    insights = insight_tool.func(ticker)

    tech = df.iloc[-1][['ma20','ma60','macd','macd_signal','macd_hist','rsi14','turnover']].to_dict()
    tech_summary = "; ".join(f"{k}:{v:.2f}" for k,v in tech.items())

    prompt = PromptTemplate.from_template(template).format(ticker=ticker, financials=fin, valuation=val, tech_summary=tech_summary, insights=insights)
    logger.info(f"已完成所有数据获取，当前数据长度为{len(prompt)}")
    logger.info(f"当前message内容为：{prompt}")
    return ds_llm.invoke(prompt)

if __name__=="__main__":
    print(analyze_company_node("600310"))
