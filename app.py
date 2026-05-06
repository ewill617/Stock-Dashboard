import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Makes it look like a wide dashboard)
st.set_page_config(page_title="Fundamental Screener", layout="wide")
st.title("📈 Fundamental Stock Screener")
st.markdown("Enter up to 5 tickers below to generate a comparative visual dashboard.")

# 2. Sidebar / User Input
st.sidebar.header("Search Parameters")
tickers_input = st.sidebar.text_input("Enter Tickers (comma separated):", "MSFT, GOOG, META, AAPL")
tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

# 3. The "Smart" Yahoo Finance Logic
@st.cache_data(ttl=3600) # Caches data so it doesn't reload every time you click a button
def get_data(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    info = t.info
    if 'shortName' not in info: return None

    # Calculate custom FNR and Rule of 40
    net_margin = info.get('profitMargins', 0)
    rev = info.get('totalRevenue', 1)
    fcf = info.get('freeCashflow', 0)
    fcf_margin = fcf / rev if rev > 0 else 0
    rev_growth = info.get('revenueGrowth', 0)

    return {
        "P/E Ratio": info.get('trailingPE', 0),
        "P/S Ratio": info.get('priceToSalesTrailing12Months', 0),
        "Op Margin %": info.get('operatingMargins', 0) * 100,
        "Net Margin %": net_margin * 100,
        "FCF Margin %": fcf_margin * 100,
        "Rev Growth %": rev_growth * 100,
        "Rule of 40 %": (fcf_margin + rev_growth) * 100,
        "FNR Percent": (net_margin + fcf_margin + rev_growth) * 100,
        "ROE %": info.get('returnOnEquity', 0) * 100
    }

# 4. Generate the Dashboard
if st.sidebar.button("Run Analysis"):
    with st.spinner("Scanning financial filings..."):
        data_dict = {t: get_data(t) for t in tickers if get_data(t)}
        
        if data_dict:
            df = pd.DataFrame(data_dict)
            
            # Top Row: The Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Custom Metric: FNR Percent")
                fig1 = px.bar(x=df.columns, y=df.loc["FNR Percent"], text_auto='.2f', color=df.columns)
                fig1.update_layout(xaxis_title="Ticker", yaxis_title="FNR (%)", showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                st.subheader("💵 Margin Comparison")
                margin_df = df.loc[["Op Margin %", "Net Margin %", "FCF Margin %"]].T
                fig2 = px.bar(margin_df, barmode='group')
                fig2.update_layout(xaxis_title="Ticker", yaxis_title="Percentage (%)")
                st.plotly_chart(fig2, use_container_width=True)

            # Bottom Row: The Data Table
            st.subheader("Full Fundamental Matrix")
            
            # Formatting the table so it looks clean
            styled_df = df.style.format("{:.2f}").background_gradient(cmap='Greens', subset=pd.IndexSlice[["Op Margin %", "Net Margin %", "FCF Margin %", "Rev Growth %", "Rule of 40 %", "FNR Percent", "ROE %"], :])
            st.dataframe(styled_df, use_container_width=True)
            
        else:
            st.error("Could not fetch data. Please check ticker symbols.")
