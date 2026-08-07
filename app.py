import streamlit as st
import pandas as pd
import pyotp
import time
from datetime import datetime, timedelta
from SmartApi import SmartConnect
from telegram_bot import send_telegram_alert

# Page Setup
st.set_page_config(page_title="Angel One EMA Scanner", layout="wide")
st.title("⚡ Angel One Multi-Timeframe EMA Crossover & Telegram Alert App")

# SIDEBAR - LOGIN & SETTINGS
st.sidebar.header("🔑 1. Angel One API Login")
api_key = st.sidebar.text_input("API Key", type="password")
client_id = st.sidebar.text_input("Client ID (Client Code)")
pin = st.sidebar.text_input("4-Digit PIN", type="password")
totp_secret = st.sidebar.text_input("TOTP Secret Key", type="password")

st.sidebar.divider()
st.sidebar.header("📲 2. Telegram Settings")
bot_token = st.sidebar.text_input("Telegram Bot Token", type="password")
chat_id = st.sidebar.text_input("Telegram Chat ID")

st.sidebar.divider()
st.sidebar.header("⚙️ 3. Scanner Settings")
timeframe_choice = st.sidebar.selectbox("Timeframe", ["1 MINUTE", "5 MINUTES", "1 HOUR"])
short_ema = st.sidebar.number_input("Short EMA (Fast)", value=9)
long_ema = st.sidebar.number_input("Long EMA (Slow)", value=21)

timeframe_map = {
    "1 MINUTE": "ONE_MINUTE",
    "5 MINUTES": "FIVE_MINUTE",
    "1 HOUR": "ONE_HOUR"
}

# CONNECT BUTTON
if st.sidebar.button("Angel One शी कनेक्ट करा"):
    if not (api_key and client_id and pin and totp_secret):
        st.sidebar.error("कृपया Angel One चे सर्व डिटेल्स भरा!")
    else:
        try:
            totp_code = pyotp.TOTP(totp_secret).now()
            smart_api = SmartConnect(api_key=api_key)
            data = smart_api.generateSession(client_id, pin, totp_code)
            
            if data['status']:
                st.session_state['smart_api'] = smart_api
                st.session_state['logged_in'] = True
                st.sidebar.success("✅ Angel One शी लॉगिन यशस्वी झाले!")
            else:
                st.sidebar.error(f"❌ लॉगिन अयशस्वी: {data['message']}")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# MAIN SCANNER LOGIC
if st.session_state.get('logged_in', False):
    smart_api = st.session_state['smart_api']
    
    st.info(f"📌 *Timeframe:* {timeframe_choice} | *Strategy:* EMA {short_ema} Crossover EMA {long_ema}")

    watch_list = [
        {"symbol": "RELIANCE-EQ", "token": "2885"},
        {"symbol": "TCS-EQ", "token": "11536"},
        {"symbol": "INFY-EQ", "token": "1594"},
        {"symbol": "HDFCBANK-EQ", "token": "1333"},
        {"symbol": "ICICIBANK-EQ", "token": "4963"},
        {"symbol": "TATAMOTORS-EQ", "token": "3456"},
        {"symbol": "SBIN-EQ", "token": "3045"},
        {"symbol": "BANKNIFTY", "token": "99926009"},
        {"symbol": "NIFTY", "token": "99926000"}
    ]

    if st.button("🚀 EMA Crossover स्कॅन सुरू करा"):
        bullish_cross = []
        bearish_cross = []

        interval_code = timeframe_map[timeframe_choice]
        days_back = 2 if timeframe_choice == "1 MINUTE" else (5 if timeframe_choice == "5 MINUTES" else 15)

        to_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d %H:%M")

        progress_bar = st.progress(0)
        total_stocks = len(watch_list)

        for idx, stock in enumerate(watch_list):
            try:
                historicParam = {
                    "exchange": "NSE",
                    "symboltoken": stock["token"],
                    "interval": interval_code,
                    "fromdate": from_date,
                    "todate": to_date
                }
                
                candles = smart_api.getCandleData(historicParam)
                
                if candles['status'] and candles['data']:
                    df = pd.DataFrame(candles['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    
                    df['EMA_Short'] = df['close'].ewm(span=short_ema, adjust=False).mean()
                    df['EMA_Long'] = df['close'].ewm(span=long_ema, adjust=False).mean()

                    prev_short = df['EMA_Short'].iloc[-2]
                    prev_long = df['EMA_Long'].iloc[-2]
                    curr_short = df['EMA_Short'].iloc[-1]
                    curr_long = df['EMA_Long'].iloc[-1]
                    last_price = df['close'].iloc[-1]
                    last_time = df['timestamp'].iloc[-1]

                    if prev_short <= prev_long and curr_short > curr_long:
                        row = {
                            "Stock": stock["symbol"], 
                            "LTP": last_price, 
                            "Time": last_time,
                            "Signal": "BUY 🟢"
                        }
                        bullish_cross.append(row)
                        
                        if bot_token and chat_id:
                            msg = (
                                f"🟢 BULLISH EMA CROSSOVER ALERT\n\n"
                                f"📈 Stock: {stock['symbol']}\n"
                                f"💵 LTP: ₹{last_price}\n"
                                f"⏱️ Timeframe: {timeframe_choice}\n"
                                f"📊 Condition: EMA {short_ema} Crossed ABOVE EMA {long_ema}\n"
                                f"🕒 Time: {last_time}"
                            )
                            send_telegram_alert(msg, bot_token, chat_id)

                    elif prev_short >= prev_long and curr_short < curr_long:
                        row = {
                            "Stock": stock["symbol"], 
                            "LTP": last_price, 
                            "Time": last_time,
                            "Signal": "SELL 🔴"
                        }
                        bearish_cross.append(row)
                        
                        if bot_token and chat_id:
                            msg = (
                                f"🔴 BEARISH EMA CROSSOVER ALERT\n\n"
                                f"📉 Stock: {stock['symbol']}\n"
                                f"💵 LTP: ₹{last_price}\n"
                                f"⏱️ Timeframe: {timeframe_choice}\n"
                                f"📊 Condition: EMA {short_ema} Crossed BELOW EMA {long_ema}\n"
                                f"🕒 Time: {last_time}"
                            )
                            send_telegram_alert(msg, bot_token, chat_id)

                time.sleep(0.3)
                progress_bar.progress((idx + 1) / total_stocks)

            except Exception:
                pass

        st.success("✅ स्कॅनिंग पूर्ण झाले!")

bullish_cross = []
bearish_cross = []

# ... तुमचा इतर स्कॅनिंगचा कोड ...

col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Bullish Crossovers (Buy)")
    if bullish_cross:
        st.dataframe(pd.DataFrame(bullish_cross))
    else:
        st.info("कोणताही बुलिश सिग्नल नाही.")

with col2:
    st.subheader("🔴 Bearish Crossovers (Sell)")
    if bearish_cross:
        st.dataframe(pd.DataFrame(bearish_cross))
    else:
        st.info("कोणताही बेअरिश सिग्नल नाही.")