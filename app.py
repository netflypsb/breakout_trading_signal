import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

# Caching the stock data fetch function to improve performance
@st.cache_data
def fetch_stock_data(ticker, period, interval):
    """
    Fetches stock data for the given ticker, period, and interval.
    """
    return yf.download(ticker, period=period, interval=interval)

# Streamlit interface setup
st.title("Breakout Trading Signal")

# User inputs
ticker = st.text_input("Enter Stock Ticker:", value="AAPL")

# Updated to include a 1-hour time frame option
timeframe_options = ["1d", "1wk", "1mo", "1h"]
timeframe = st.selectbox("Select Time Frame:", options=timeframe_options, index=3)

# Updated to include a 1-month period option
period_options = ["1mo", "3mo", "6mo", "1y", "2y"]
period = st.selectbox("Select Period:", options=period_options, index=0)

analyze_button = st.button("Analyze Breakout Points")

if analyze_button:
    try:
        # Fetching the stock data with the selected period and interval
        stock_data = fetch_stock_data(ticker, period, timeframe)

        if not stock_data.empty:
            # Calculating technical indicators
            stock_data['SMA9'] = ta.sma(stock_data['Close'], length=9)
            stock_data['SMA20'] = ta.sma(stock_data['Close'], length=20)
            stock_data['SMA50'] = ta.sma(stock_data['Close'], length=50)
            stock_data['SMA200'] = ta.sma(stock_data['Close'], length=200)
            stock_data['RSI'] = ta.rsi(stock_data['Close'], length=14)
            macd = ta.macd(stock_data['Close'])
            stock_data['MACD'] = macd['MACD_12_26_9']
            stock_data['MACDSignal'] = macd['MACDs_12_26_9']

            # Adding volume moving average for comparison
            stock_data['Volume_MA20'] = ta.sma(stock_data['Volume'], length=20)

            # Identifying breakout points for all three logics with volume increase criterion
            crossover_points_logic1 = stock_data[(stock_data['SMA9'] > stock_data['SMA20']) & (stock_data['SMA9'].shift(1) < stock_data['SMA20'].shift(1)) & (stock_data['Volume'] > stock_data['Volume_MA20'])]
            crossover_points_logic2 = stock_data[(stock_data['SMA20'] > stock_data['SMA50']) & (stock_data['SMA20'].shift(1) < stock_data['SMA50'].shift(1)) & (stock_data['Volume'] > stock_data['Volume_MA20'])]
            crossover_points_original = stock_data[(stock_data['SMA50'] > stock_data['SMA200']) & (stock_data['SMA50'].shift(1) < stock_data['SMA200'].shift(1)) & (stock_data['Volume'] > stock_data['Volume_MA20'])]

            # Plotting
            fig, ax = plt.subplots(3, 1, figsize=(10, 15), sharex=True)

            # Price, SMAs, and breakout points for all logics
            ax[0].plot(stock_data['Close'], label='Close Price', color='skyblue')
            ax[0].plot(stock_data['SMA9'], label='9-Day SMA', color='orange')
            ax[0].plot(stock_data['SMA20'], label='20-Day SMA', color='purple')
            ax[0].plot(stock_data['SMA50'], label='50-Day SMA', color='green')
            ax[0].plot(stock_data['SMA200'], label='200-Day SMA', color='red')
            ax[0].scatter(crossover_points_logic1.index, crossover_points_logic1['Close'], color='gold', label='Logic 1 Breakouts', zorder=5)
            ax[0].scatter(crossover_points_logic2.index, crossover_points_logic2['Close'], color='violet', label='Logic 2 Breakouts', zorder=5)
            ax[0].scatter(crossover_points_original.index, crossover_points_original['Close'], color='magenta', label='Original Logic Breakouts', zorder=5)
            ax[0].set_title(f"{ticker} Price and SMA Breakout Points Analysis")
            ax[0].legend() 

# Volume and Volume MA
            ax[1].bar(stock_data.index, stock_data['Volume'], label='Volume', color='gray', alpha=0.3)
            ax[1].plot(stock_data['Volume_MA20'], label='20-Day Volume MA', color='orange')
            ax[1].scatter(crossover_points_logic1.index, crossover_points_logic1['Volume'], color='gold', label='SMA 9/20 Breakouts', zorder=5)
            ax[1].scatter(crossover_points_logic2.index, crossover_points_logic2['Volume'], color='violet', label='SMA 20/50 Breakouts', zorder=5)
            ax[1].scatter(crossover_points_original.index, crossover_points_original['Volume'], color='magenta', label='SMA 50/200 Breakouts', zorder=5)
            ax[1].set_title(f"{ticker} Volume and Breakout Points")
            ax[1].legend()

            # RSI and MACD
            ax[2].plot(stock_data['RSI'], label='RSI', color='purple')
            ax[2].axhline(70, linestyle='--', color='grey', alpha=0.5, label='Overbought')
            ax[2].axhline(30, linestyle='--', color='grey', alpha=0.5, label='Oversold')
            ax[2].plot(stock_data['MACD'], label='MACD', color='blue')
            ax[2].plot(stock_data['MACDSignal'], label='MACD Signal', color='orange')
            ax[2].set_title(f"{ticker} RSI & MACD")
            ax[2].legend()

            # Display plot in Streamlit
            st.pyplot(fig)
        else:
            st.error("No data found for the specified ticker. Please try another ticker.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

