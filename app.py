import os
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import pyotp
import requests
from SmartApi import SmartConnect
import streamlit as st
import ta
import yfinance as yf

# ---- ANGEL ONE CONFIGURATION (फक्त एकदाच सेव्ह करा) ----
ANGEL_API_KEY = "तुमची_API_KEY_इथे_टाका"
ANGEL_CLIENT_CODE = "तुमचा_CLIENT_CODE_इथे_टाका"
ANGEL_TOTP_KEY = "तुमची_TOTP_SECRET_KEY_इथे_टाका"  # Google Authenticator TOTP Key

TG_TOKEN = "8799046332:AAHzWmvR1ZWJ-7ARzWgybFu-6Ykl7Trdt2k"
TG_CHAT_ID = "5055029691"

# ---- PAGE CONFIGURATION ----
st.set_page_config(
    page_title="Market Analyser - Angel One Live",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ---- ULTRA VIBRANT NEON CSS (PURE BLACK THEME) ----
st.markdown(
    """
<style>
    .stApp {
        background-color: #05070a;
        color: #e6edf3;
    }
    
    /* Branding Header Box */
    .branding-box {
        text-align: center;
        margin-top: 5px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        background: #000000;
        padding: 15px;
        border-radius: 16px;
        border: 1px solid #1f242c;
    }

    /* Top Name: HULGUNDE */
    .neon-hulgunde-extended {
        display: flex;
        justify-content: space-between;
        width: 100%;
        max-width: 580px;
        margin-top: 5px;
        margin-bottom: 2px;
        font-size: 2.4rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 6px;
    }

    .h-pink   { color: #FF007A; text-shadow: 0 0 15px #FF007A; }
    .h-orange { color: #FF7700; text-shadow: 0 0 15px #FF7700; }
    .h-yellow { color: #FFE600; text-shadow: 0 0 15px #FFE600; }
    .h-green  { color: #00FF88; text-shadow: 0 0 15px #00FF88; }
    .h-cyan   { color: #00F0FF; text-shadow: 0 0 15px #00F0FF; }
    .h-blue   { color: #388BFD; text-shadow: 0 0 15px #388BFD; }
    .h-purple { color: #9D00FF; text-shadow: 0 0 15px #9D00FF; }
    .h-magenta{ color: #FF00D4; text-shadow: 0 0 15px #FF00D4; }

    /* Bottom Name: MARKET ANALYSER */
    .neon-market-analyser {
        background: linear-gradient(135deg, #00F0FF 0%, #9D00FF 50%, #FF007A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.6rem;
        font-weight: 900;
        text-align: center;
        text-shadow: 0 0 25px rgba(0, 240, 255, 0.45);
        letter-spacing: 3px;
        margin-top: 2px;
        margin-bottom: 5px;
        line-height: 1.2;
    }

    .neon-subtitle-center {
        color: #58a6ff;
        font-size: 1rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Angel One Style Commodity Cards */
    .angel-card {
        background: #0d1117;
        border: 1px solid #21262d;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        margin-bottom: 15px;
    }
    .angel-card-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.5px;
    }
    .angel-tag {
        background: #161b22;
        color: #8b949e;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        display: inline-block;
        margin-top: 4px;
        margin-bottom: 10px;
    }
    .angel-price-up {
        font-size: 1.6rem;
        font-weight: 800;
        color: #00FF88;
    }
    .angel-price-down {
        font-size: 1.6rem;
        font-weight: 800;
        color: #FF0055;
    }

    /* Glowing Yellow Labels */
    .yellow-glow-label {
        color: #FFE600 !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 10px rgba(255, 230, 0, 0.6) !important;
        margin-bottom: 6px;
        display: block;
    }

    /* Stat Metric Cards */
    .card-pink {
        background: linear-gradient(135deg, #160718 0%, #240822 100%);
        border: 2px solid #FF007A;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 0 15px rgba(255, 0, 122, 0.3);
    }
    .card-yellow {
        background: linear-gradient(135deg, #1c1604 0%, #2b2207 100%);
        border: 2px solid #FFE600;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 0 18px rgba(255, 230, 0, 0.4);
    }
    .card-green {
        background: linear-gradient(135deg, #05140c 0%, #0a2416 100%);
        border: 2px solid #00FF88;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
    }
    
    .val-pink { font-size: 1.8rem; font-weight: 800; color: #FF66B2; }
    .val-yellow { font-size: 1.8rem; font-weight: 800; color: #FFE600; }
    .val-green { font-size: 1.8rem; font-weight: 800; color: #00FF88; }
    .card-lbl { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; margin-top: 4px; }

    /* Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #FF007A 0%, #9D00FF 50%, #00F0FF 100%);
        color: #ffffff;
        font-weight: 800;
        font-size: 1.05rem;
        border-radius: 10px;
        border: none;
        padding: 0.7rem 2.2rem;
        box-shadow: 0 0 20px rgba(255, 0, 122, 0.45);
        transition: all 0.3s ease;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---- MASTER WATCHLIST (NSE & ANGEL TOKENS) ----
MARKET_SECTORS = {
    "🔥 NIFTY 50": [
        "ADANIENT.NS",
        "ADANIPORTS.NS",
        "ASIANPAINT.NS",
        "AXISBANK.NS",
        "BAJFINANCE.NS",
        "BAJAJFINSV.NS",
        "BHARTIARTL.NS",
        "CIPLA.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "INFY.NS",
        "ITC.NS",
        "JSWSTEEL.NS",
        "KOTAKBANK.NS",
        "LT.NS",
        "M&M.NS",
        "MARUTI.NS",
        "NTPC.NS",
        "ONGC.NS",
        "POWERGRID.NS",
        "RELIANCE.NS",
        "SBIN.NS",
        "SUNPHARMA.NS",
        "TATAMOTORS.NS",
        "TATASTEEL.NS",
        "TCS.NS",
        "TITAN.NS",
        "WIPRO.NS",
    ],
    "🏦 BANKNIFTY": [
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "KOTAKBANK.NS",
        "AXISBANK.NS",
        "INDUSINDBK.NS",
        "BANKBARODA.NS",
        "PNB.NS",
        "AUBANK.NS",
        "FEDERALBNK.NS",
        "IDFCFIRSTB.NS",
    ],
    "💳 FINNIFTY": [
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "KOTAKBANK.NS",
        "AXISBANK.NS",
        "SBIN.NS",
        "BAJFINANCE.NS",
        "BAJAJFINSV.NS",
        "HDFCLIFE.NS",
        "SBILIFE.NS",
        "CHOLAFIN.NS",
        "SHRIRAMFIN.NS",
    ],
    "🛢️ TOP COMMODITIES": ["CL=F", "GC=F", "GOLDBEES.NS"],
}

# ---- ANGEL ONE SESSION HANDLER ----
if "smart_api" not in st.session_state:
  st.session_state["smart_api"] = None

# ---- SIDEBAR CONTROLS ----
with st.sidebar:
  st.markdown("## 🌈 *कंट्रोल सेंटर*")

  # Angel One MPIN Input Section
  st.markdown(
      '<span class="yellow-glow-label">🔑 Angel One Quick Login</span>',
      unsafe_allow_html=True,
  )
  user_mpin = st.text_input(
      "MPIN टाका:",
      type="password",
      max_chars=6,
      placeholder="4-digit PIN",
      label_visibility="collapsed",
  )

  if user_mpin and st.session_state["smart_api"] is None:
    try:
      smart_api = SmartConnect(api_key=ANGEL_API_KEY)
      auto_totp = pyotp.TOTP(ANGEL_TOTP_KEY).now()
      session_data = smart_api.generateSession(
          ANGEL_CLIENT_CODE, user_mpin, auto_totp
      )
      if session_data.get("status"):
        st.session_state["smart_api"] = smart_api
        st.success("⚡ Angel One Live Connected!")
      else:
        st.error("❌ चुकीचा MPIN!")
    except Exception:
      st.warning("⚠️ API Key/Secret तपासा.")

  if st.session_state["smart_api"]:
    st.markdown("🟢 *Status:* Angel One API Live")
  else:
    st.markdown("⚪ *Status:* Default Live Feed Active")

  st.markdown("---")
  selected_market = st.selectbox(
      "🎯 इंडेक्स / कमॉडिटी निवडा:", list(MARKET_SECTORS.keys())
  )
  selected_stocks = MARKET_SECTORS[selected_market]

  st.markdown(
      '<span class="yellow-glow-label">⏱️ Timeframe</span>',
      unsafe_allow_html=True,
  )
  timeframe = st.select_slider(
      "Timeframe Selector",
      options=["1m", "5m", "15m", "1h", "1d"],
      value="15m",
      label_visibility="collapsed",
  )

  st.markdown(
      '<span class="yellow-glow-label">📈 EMA Indicators</span>',
      unsafe_allow_html=True,
  )
  selected_emas = st.multiselect(
      "EMA Selector",
      [9, 21, 50, 200],
      default=[9, 21, 50, 200],
      label_visibility="collapsed",
  )

  st.markdown(
      '<span class="yellow-glow-label">🎯 Support & Resistance</span>',
      unsafe_allow_html=True,
  )
  check_sr = st.checkbox("Support & Resistance लेव्हल्स दाखवा", value=True)

  st.markdown("---")
  st.markdown("### ✈️ Telegram बॉट")
  tg_token = st.text_input(
      "Bot Token",
      value="8799046332:AAHzWmvR1ZWJ-7ARzWgybFu-6Ykl7Trdt2k",
      type="password",
  )
  tg_chat_id = st.text_input("Chat ID", value="5055029691")

# ---- MAIN DASHBOARD: CENTER BRANDING HEADER ----
h_col1, h_col2, h_col3 = st.columns([1, 2.2, 1])
with h_col2:
  if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)

st.markdown(
    """
<div class="branding-box">
    <div class="neon-hulgunde-extended">
        <span class="h-pink">H</span>
        <span class="h-orange">U</span>
        <span class="h-yellow">L</span>
        <span class="h-green">G</span>
        <span class="h-cyan">U</span>
        <span class="h-blue">N</span>
        <span class="h-purple">D</span>
        <span class="h-magenta">E</span>
    </div>
    <div class="neon-market-analyser">MARKET ANALYSER</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="neon-subtitle-center">🚀 लाईव्ह मल्टि-ॲसेट ॲनालिसिस • <b>{selected_market}</b> • Timeframe: <b>{timeframe}</b></div>',
    unsafe_allow_html=True,
)

# ---- ANGEL ONE STYLE TOP COMMODITY CARDS ----
com_col1, com_col2 = st.columns(2)
with com_col1:
  st.markdown(
      """
    <div class="angel-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="angel-card-title">🛢️ CRUDE OIL</div>
            <span style="color:#00FF88; font-size:0.8rem; font-weight:700;">● LIVE MCX</span>
        </div>
        <div class="angel-tag">Options Expiry 17 Sep</div>
        <div class="angel-price-down">₹8,132.00 ▼</div>
        <div style="color:#FF0055; font-size:0.85rem; font-weight:600;">-₹227.00 (-2.72%)</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

with com_col2:
  st.markdown(
      """
    <div class="angel-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="angel-card-title">🪙 GOLD</div>
            <span style="color:#00FF88; font-size:0.8rem; font-weight:700;">● LIVE MCX</span>
        </div>
        <div class="angel-tag">Options Expiry 31 Aug</div>
        <div class="angel-price-up">₹1,63,678.00 ▲</div>
        <div style="color:#00FF88; font-size:0.85rem; font-weight:600;">+₹1,240.00 (+0.76%)</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

# 4 Stat Metric Cards
c1, c2, c3, c4 = st.columns(4)
c1.markdown(
    f'<div class="card-pink"><div class="val-pink">{len(selected_stocks)}</div><div class="card-lbl">एकूण शेअर्स</div></div>',
    unsafe_allow_html=True,
)
c2.markdown(
    f'<div class="card-yellow"><div class="val-yellow">{timeframe}</div><div class="card-lbl">Timeframe</div></div>',
    unsafe_allow_html=True,
)
c3.markdown(
    f'<div class="card-yellow"><div class="val-yellow">{len(selected_emas)} EMAs</div><div class="card-lbl">Indicators</div></div>',
    unsafe_allow_html=True,
)
c4.markdown(
    '<div class="card-green"><div class="val-green">24/7 LIVE</div><div class="card-lbl">ऑटोमेशन स्टेटस</div></div>',
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(
    ["⚡ थेट ब्रेकआऊट सिग्नल्स (Live Signals)", "🕯️ मल्टिकलर निऑन चार्ट"]
)

period_map = {"1m": "5d", "5m": "10d", "15m": "30d", "1h": "60d", "1d": "1y"}


@st.cache_data(ttl=60)
def fetch_and_calculate(symbol, tf):
  try:
    df = yf.download(
        symbol, period=period_map.get(tf, "30d"), interval=tf, progress=False
    )
    if isinstance(df.columns, pd.MultiIndex):
      df.columns = [col[0] for col in df.columns]
    if len(df) < 50:
      return None

    for ema in [9, 21, 50, 200]:
      df[f"EMA_{ema}"] = ta.trend.ema_indicator(df["Close"], window=ema)

    df["Resistance"] = df["High"].rolling(20).max()
    df["Support"] = df["Low"].rolling(20).min()
    return df
  except Exception:
    return None


with tab1:
  if st.button("🔥 आता त्वरित स्कॅन करा (Instant Scan)"):
    results = []
    bar = st.progress(0)

    for idx, sym in enumerate(selected_stocks):
      bar.progress((idx + 1) / len(selected_stocks))
      df = fetch_and_calculate(sym, timeframe)
      if df is None or len(df) < 2:
        continue

      c_close = float(df["Close"].iloc[-1])
      p_close = float(df["Close"].iloc[-2])
      res_lvl = float(df["Resistance"].iloc[-2])
      sup_lvl = float(df["Support"].iloc[-2])

      signals = []
      for ema in selected_emas:
        if f"EMA_{ema}" in df.columns:
          p_ema = float(df[f"EMA_{ema}"].iloc[-2])
          c_ema = float(df[f"EMA_{ema}"].iloc[-1])
          if p_close <= p_ema and c_close > c_ema:
            signals.append(f"🟢 BUY (Above {ema} EMA)")
          elif p_close >= p_ema and c_close < c_ema:
            signals.append(f"🔴 SELL (Below {ema} EMA)")

      if check_sr:
        if c_close > res_lvl and p_close <= res_lvl:
          signals.append("🚀 RESISTANCE BREAKOUT")
        elif c_close < sup_lvl and p_close >= sup_lvl:
          signals.append("⚠️ SUPPORT BREAKDOWN")

      if signals:
        clean_name = (
            sym.replace(".NS", "")
            .replace(".BO", "")
            .replace("CL=F", "CRUDE OIL")
            .replace("GC=F", "GOLD")
        )
        results.append({
            "Stock / Commodity": clean_name,
            "CMP (₹)": f"₹{c_close:.2f}",
            "Technical Signals": "  |  ".join(signals),
            "Support (₹)": f"₹{sup_lvl:.2f}",
            "Resistance (₹)": f"₹{res_lvl:.2f}",
        })

    bar.empty()
    if results:
      res_df = pd.DataFrame(results)
      st.success(f"🎉 एकूण {len(results)} शेअर्समध्ये सिग्नल्स मिळाले!")
      st.dataframe(res_df, use_container_width=True, hide_index=True)
    else:
      st.info("या टाइमफ्रेमवर सध्या कोणताही नवीन सिग्नल उपलब्ध नाही.")

with tab2:
  chart_sym = st.selectbox("📊 विश्लेषणासाठी निवडा:", selected_stocks)
  df_chart = fetch_and_calculate(chart_sym, timeframe)

  if df_chart is not None:
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df_chart.index,
            open=df_chart["Open"],
            high=df_chart["High"],
            low=df_chart["Low"],
            close=df_chart["Close"],
            name="कँडल्स",
            increasing_line_color="#00FF88",
            decreasing_line_color="#FF0055",
        )
    )

    ema_colors = {
        9: "#FFE600",
        21: "#00F0FF",
        50: "#FF00AA",
        200: "#9D00FF",
    }

    for ema in selected_emas:
      if f"EMA_{ema}" in df_chart.columns:
        fig.add_trace(
            go.Scatter(
                x=df_chart.index,
                y=df_chart[f"EMA_{ema}"],
                name=f"EMA {ema}",
                line=dict(color=ema_colors.get(ema, "#FFFFFF"), width=2),
            )
        )

    if check_sr:
      latest_res = df_chart["Resistance"].iloc[-1]
      latest_sup = df_chart["Support"].iloc[-1]
      fig.add_hline(
          y=latest_res,
          line_dash="dash",
          line_color="#00F0FF",
          annotation_text=f"Res: ₹{latest_res:.2f}",
          annotation_font_color="#00F0FF",
      )
      fig.add_hline(
          y=latest_sup,
          line_dash="dash",
          line_color="#FF007A",
          annotation_text=f"Sup: ₹{latest_sup:.2f}",
          annotation_font_color="#FF007A",
      )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#05070a",
        paper_bgcolor="#05070a",
        xaxis_rangeslider_visible=False,
        height=580,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
