import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="NSE Momentum Screen", layout="wide")

st.title("🚀 NSE Momentum Dashboard")
st.write("Criteria: EMA 3 > 5 > 10 > 20 | Green Candle | >5Cr Vol")

def get_data():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    symbols = [s + ".NS" for s in pd.read_csv(url)['Symbol'].tolist()]
    
    screened = []
    progress_bar = st.progress(0)
    
    for i, ticker in enumerate(symbols[:100]): # Test with 100 first for speed
        try:
            df = yf.download(ticker, period="1mo", interval="1d", progress=False)
            if len(df) < 20: continue

            df['E3'] = df['Close'].ewm(span=3, adjust=False).mean()
            df['E5'] = df['Close'].ewm(span=5, adjust=False).mean()
            df['E10'] = df['Close'].ewm(span=10, adjust=False).mean()
            df['E20'] = df['Close'].ewm(span=20, adjust=False).mean()

            last = df.iloc[-1]
            val_cr = (last['Close'] * last['Volume']) / 10000000

            if (last['E3'] > last['E5'] > last['E10'] > last['E20']) and \
               (last['Close'] > last['Open']) and (val_cr > 5):
                
                screened.append({
                    "Symbol": ticker.replace(".NS", ""),
                    "Price": round(last['Close'], 2),
                    "Value(Cr)": round(val_cr, 2),
                    "Gap20%": round(((last['Close'] - last['E20'])/last['E20'])*100, 2)
                })
            progress_bar.progress((i + 1) / 100)
        except: continue
    return pd.DataFrame(screened)

if st.button('Run Scanner'):
    results = get_data()
    if not results.empty:
        st.dataframe(results.sort_values("Gap20%"), use_container_width=True)
    else:
        st.write("No stocks found meeting criteria.")
