import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 网页配置
st.set_page_config(page_title="利弗莫尔操盘助手", layout="centered")

st.title("📈 利弗莫尔趋势工具")
st.caption("基于《股票做手回忆录》核心逻辑：趋势 + 关键点")

# 侧边栏配置
st.sidebar.header("交易设置")
symbol = st.sidebar.text_input("股票代码 (美股如 AAPL, A股如 000001.SS)", "NVDA")
stop_loss_pct = st.sidebar.slider("强制止损比例 (%)", 5, 15, 10)

# 获取数据
@st.cache_data(ttl=3600)
def load_stock_data(ticker):
    try:
        data = yf.download(ticker, period="1y")
        return data
    except:
        return None

data = load_stock_data(symbol)

if data is not None and not data.empty:
    # 核心指标计算
    curr_price = float(data['Close'].iloc[-1])
    ma200 = float(data['Close'].rolling(window=200).mean().iloc[-1])
    # 关键点（过去20个交易日的最高点，不含今天）
    pivotal_point = float(data['High'].rolling(window=20).max().iloc[-2])
    
    # 顶部状态看板
    col1, col2 = st.columns(2)
    col1.metric("当前价格", f"{curr_price:.2f}")
    col2.metric("200日牛熊线", f"{ma200:.2f}")

    # 信号判断逻辑
    st.subheader("📊 操盘指令")
    if curr_price > ma200:
        if curr_price > pivotal_point:
            st.success(f"🔥 **突破信号**：已突破关键点 {pivotal_point:.2f}！最小阻力线向上，建议建立首笔仓位。")
            st.info(f"🚩 初始止损建议：{curr_price * (1 - stop_loss_pct/100):.2f}")
        else:
            st.warning(f"⏳ **观望**：大趋势（200日线）看多，但价格未突破关键点 {pivotal_point:.2f}。利弗莫尔建议：等待。")
    else:
        st.error("❌ **禁区**：价格位于200日线下，属于弱势市场，不符合买入原则。")

    # 简易K线图
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='K线')])
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(window=200).mean(), name='200日线', line=dict(color='orange')))
    fig.update_layout(xaxis_rangeslider_visible=False, height=400, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("无法加载数据，请确保代码输入正确（如：苹果 AAPL，腾讯 0700.HK，茅台 600519.SS）。")
