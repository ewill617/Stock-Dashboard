import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ultimate Fundamental Screener", layout="wide")
st.title("📈 Ultimate Fundamental Screener")
st.markdown("Comprehensive analysis of Stock Performance, Income, Balance Sheet, and custom metrics.")

st.sidebar.header("Search Parameters")
tickers_input = st.sidebar.text_input("Enter Tickers (comma separated):", "MSFT, GOOG, META, AAPL")
tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

@st.cache_data(ttl=3600)
def get_data(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    info = t.info
    if 'shortName' not in info: return None

    # Deep dive into Balance Sheet and Cash Flow for hidden metrics
    try:
        bs = t.balance_sheet
        is_stmt = t.income_stmt
        
        # Total Assets vs Liabilities
        total_assets = bs.loc['Total Assets'].iloc[0] if 'Total Assets' in bs.index else 0
        total_liab = bs.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in bs.index else 0
        asset_liab_ratio = total_assets / total_liab if total_liab > 0 else 0
        
        # ROIC Calculation
        net_income = is_stmt.loc['Net Income'].iloc[0] if 'Net Income' in is_stmt.index else 0
        total_debt = bs.loc['Total Debt'].iloc[0] if 'Total Debt' in bs.index else 0
        equity = bs.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in bs.index else 0
        roic = net_income / (total_debt + equity) if (total_debt + equity) > 0 else 0
    except:
        asset_liab_ratio = 0
        roic = 0

    # Margins and Growth
    net_margin = info.get('profitMargins', 0)
    rev = info.get('totalRevenue', 1)
    fcf = info.get('freeCashflow', 0)
    fcf_margin = fcf / rev if rev > 0 else 0
    rev_growth = info.get('revenueGrowth', 0)
    
    # Per Share Data
    eps = info.get('trailingEps', 0)
    price = info.get('currentPrice', 1)
    earnings_yield = (eps / price) if price > 0 else 0

    return {
        # --- STOCK PERFORMANCE ---
        "P/E Ratio": info.get('trailingPE', 0),
        "P/S Ratio": info.get('priceToSalesTrailing12Months', 0),
        "Forward P/E": info.get('forwardPE', 0),
        
        # --- INCOME STATEMENT ---
        "Op Margin %": info.get('operatingMargins', 0) * 100,
        "Net Margin %": net_margin * 100,
        "FCF Margin %": fcf_margin * 100,
        
        # --- BALANCE SHEET & CAPITAL ---
        "Current Ratio": info.get('currentRatio', 0),
        "Debt to Equity": info.get('debtToEquity', 0),
        "Asset/Liab Ratio": asset_liab_ratio,
        "Price/Book (Value)": info.get('priceToBook', 0),
        
        # --- PER SHARE DATA ---
        "Rev Per Share": info.get('revenuePerShare', 0),
        "EPS": eps,
        "Earnings Yield %": earnings_yield * 100,
        
        # --- KEY METRICS & CUSTOM ---
        "Rev Growth YoY %": rev_growth * 100,
        "Rule of 40 %": (fcf_margin + rev_growth) * 100,
        "FNR Percent": (net_margin + fcf_margin + rev_growth) * 100,
        
        # --- MANAGEMENT EFFECTIVENESS ---
        "ROE %": info.get('returnOnEquity', 0) * 100,
        "ROA %": info.get('returnOnAssets', 0) * 100,
        "ROIC %": roic * 100
    }

if st.sidebar.button("Run Analysis"):
    with st.spinner("Deep scanning financial filings..."):
        data_dict = {t: get_data(t) for t in tickers if get_data(t)}
        
        if data_dict:
            df = pd.DataFrame(data_dict)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🏆 Custom FNR Showdown")
                fig1 = px.bar(x=df.columns, y=df.loc["FNR Percent"], text_auto='.2f', color=df.columns)
                fig1.update_layout(xaxis_title="Ticker", yaxis_title="FNR (%)", showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                st.subheader("⚖️ Asset/Liability Health (Ideal > 1)")
                fig2 = px.bar(x=df.columns, y=df.loc["Asset/Liab Ratio"], text_auto='.2f', color=df.columns)
                fig2.update_layout(xaxis_title="Ticker", yaxis_title="Total Assets / Total Liab", showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            st.subheader("The Full Fundamental Matrix")
            
            # Traffic Light Scheme: Green is Good, Yellow is Average, Red is Bad
            styled_df = df.style.format("{:.2f}") \
                .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[["Op Margin %", "Net Margin %", "FCF Margin %", "Rev Growth YoY %", "Rule of 40 %", "FNR Percent", "ROE %", "ROA %", "ROIC %", "Asset/Liab Ratio", "Earnings Yield %"], :]) \
                .background_gradient(cmap='RdYlGn_r', subset=pd.IndexSlice[["P/E Ratio", "P/S Ratio", "Debt to Equity", "Price/Book (Value)"], :])
            
            st.dataframe(styled_df, use_container_width=True, height=600)
