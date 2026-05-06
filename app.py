import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Fundamental Screener", page_icon="🏦", layout="wide")

# 2. Sidebar & Expanders
with st.sidebar:
    st.title("🏦 Screener Settings")
    tickers_input = st.text_input("Enter Tickers (comma separated):", "MSFT")
    tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
    analyze_button = st.button("Run Analysis", type="primary", use_container_width=True)
    
    with st.expander("ℹ️ How to use this tool"):
        st.write("Type ONE ticker for a deep-dive profile, or MULTIPLE tickers for a comparative dashboard.")

# 3. Data Engine
@st.cache_data(ttl=3600)
def get_data(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    info = t.info
    if 'shortName' not in info: return None

    try:
        bs = t.balance_sheet
        is_stmt = t.income_stmt
        total_assets = bs.loc['Total Assets'].iloc[0] if 'Total Assets' in bs.index else 0
        total_liab = bs.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in bs.index else 0
        asset_liab_ratio = total_assets / total_liab if total_liab > 0 else 0
        net_income = is_stmt.loc['Net Income'].iloc[0] if 'Net Income' in is_stmt.index else 0
        total_debt = bs.loc['Total Debt'].iloc[0] if 'Total Debt' in bs.index else 0
        equity = bs.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in bs.index else 0
        roic = net_income / (total_debt + equity) if (total_debt + equity) > 0 else 0
    except:
        asset_liab_ratio = 0; roic = 0

    net_margin = info.get('profitMargins', 0)
    rev = info.get('totalRevenue', 1)
    fcf = info.get('freeCashflow', 0)
    fcf_margin = fcf / rev if rev > 0 else 0
    rev_growth = info.get('revenueGrowth', 0)
    eps = info.get('trailingEps', 0)
    price = info.get('currentPrice', 1)
    earnings_yield = (eps / price) if price > 0 else 0

    return {
        "P/E Ratio": info.get('trailingPE', 0),
        "P/S Ratio": info.get('priceToSalesTrailing12Months', 0),
        "Forward P/E": info.get('forwardPE', 0),
        "Op Margin %": info.get('operatingMargins', 0) * 100,
        "Net Margin %": net_margin * 100,
        "FCF Margin %": fcf_margin * 100,
        "Current Ratio": info.get('currentRatio', 0),
        "Debt to Equity": info.get('debtToEquity', 0),
        "Asset/Liab Ratio": asset_liab_ratio,
        "Price/Book (Value)": info.get('priceToBook', 0),
        "Rev Per Share": info.get('revenuePerShare', 0),
        "EPS": eps,
        "Earnings Yield %": earnings_yield * 100,
        "Rev Growth YoY %": rev_growth * 100,
        "Rule of 40 %": (fcf_margin + rev_growth) * 100,
        "FNR Percent": (net_margin + fcf_margin + rev_growth) * 100,
        "ROE %": info.get('returnOnEquity', 0) * 100,
        "ROA %": info.get('returnOnAssets', 0) * 100,
        "ROIC %": roic * 100
    }

# 4. Main App Layout
st.title("Fundamental Moat & Margin Screener")

if analyze_button or tickers:
    with st.spinner("Scanning financial filings..."):
        data_dict = {t: get_data(t) for t in tickers if get_data(t)}
        valid_tickers = list(data_dict.keys())
        
        if not valid_tickers:
            st.error("Could not fetch data. Please check ticker symbols.")
            
        # ==========================================
        # UI MODE 1: SINGLE TIER TEAR SHEET
        # ==========================================
        elif len(valid_tickers) == 1:
            t = valid_tickers[0]
            data = data_dict[t]
            
            st.markdown(f"## 🏢 Deep Dive Profile: **{t}**")
            st.divider()
            
            # Row 1: Moat & Profitability
            st.subheader("🛡️ Moat & Profitability")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("FNR Percent", f"{data['FNR Percent']:.2f}%")
            m2.metric("Rule of 40", f"{data['Rule of 40 %']:.2f}%")
            m3.metric("FCF Margin", f"{data['FCF Margin %']:.2f}%")
            m4.metric("ROIC", f"{data['ROIC %']:.2f}%")
            
            st.write("") # Spacer
            
            # Row 2: Balance Sheet Health
            st.subheader("⚖️ Balance Sheet Health")
            h1, h2, h3, h4 = st.columns(4)
            h1.metric("Asset/Liab Ratio", f"{data['Asset/Liab Ratio']:.2f}")
            h2.metric("Debt to Equity", f"{data['Debt to Equity']:.2f}")
            h3.metric("Current Ratio", f"{data['Current Ratio']:.2f}")
            h4.metric("Rev Growth YoY", f"{data['Rev Growth YoY %']:.2f}%")
            
            st.write("") # Spacer
            
            # Row 3: Valuation & Price
            st.subheader("🏷️ Valuation & Price")
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("P/E Ratio", f"{data['P/E Ratio']:.2f}")
            v2.metric("Forward P/E", f"{data['Forward P/E']:.2f}")
            v3.metric("P/S Ratio", f"{data['P/S Ratio']:.2f}")
            v4.metric("Earnings Yield", f"{data['Earnings Yield %']:.2f}%")
            
            # Row 4: Extra Details
            st.write("") # Spacer
            with st.expander("View Additional Raw Metrics"):
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("Net Margin %", f"{data['Net Margin %']:.2f}%")
                e2.metric("Op Margin %", f"{data['Op Margin %']:.2f}%")
                e3.metric("Price/Book", f"{data['Price/Book (Value)']:.2f}")
                e4.metric("EPS", f"${data['EPS']:.2f}")

        # ==========================================
        # UI MODE 2: MULTI-STOCK COMPARISON
        # ==========================================
        else:
            df = pd.DataFrame(data_dict)
            
            # Top KPI Cards
            st.markdown("### Top Performers Overview")
            kpi1, kpi2, kpi3 = st.columns(3)
            
            best_fnr_ticker = df.loc["FNR Percent"].idxmax()
            best_al_ticker = df.loc["Asset/Liab Ratio"].idxmax()
            best_fcf_ticker = df.loc["FCF Margin %"].idxmax()

            kpi1.metric(label="🏆 Highest FNR Percent", value=best_fnr_ticker, delta=f"{df.loc['FNR Percent'].max():.2f}%", delta_color="normal")
            kpi2.metric(label="🛡️ Best Asset/Liab Ratio", value=best_al_ticker, delta=f"{df.loc['Asset/Liab Ratio'].max():.2f}", delta_color="normal")
            kpi3.metric(label="💸 Best FCF Margin", value=best_fcf_ticker, delta=f"{df.loc['FCF Margin %'].max():.2f}%", delta_color="normal")
            
            st.divider()

            # Tabs Layout
            tab1, tab2 = st.tabs(["📊 Visual Comparisons", "🧮 Full Data Matrix"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.bar(x=df.columns, y=df.loc["FNR Percent"], text_auto='.2f', color=df.columns, title="Custom FNR Showdown")
                    fig1.update_layout(xaxis_title="", yaxis_title="FNR (%)", showlegend=False)
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    fig2 = px.bar(x=df.columns, y=df.loc["Asset/Liab Ratio"], text_auto='.2f', color=df.columns, title="Asset/Liability Health (Ideal > 1)")
                    fig2.update_layout(xaxis_title="", yaxis_title="Ratio", showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)

            with tab2:
                display_df = df.apply(lambda x: x.map(lambda y: f"{y:.2f}"))
                max_metrics = ["Op Margin %", "Net Margin %", "FCF Margin %", "Current Ratio", "Asset/Liab Ratio", "Rev Per Share", "EPS", "Earnings Yield %", "Rev Growth YoY %", "Rule of 40 %", "FNR Percent", "ROE %", "ROA %", "ROIC %"]
                min_metrics = ["P/E Ratio", "P/S Ratio", "Forward P/E", "Debt to Equity", "Price/Book (Value)"]

                for metric in df.index:
                    row_data = df.loc[metric]
                    best_ticker = None
                    if metric in max_metrics: best_ticker = row_data.idxmax()
                    elif metric in min_metrics: best_ticker = row_data.idxmin()

                    if best_ticker and pd.notna(row_data[best_ticker]):
                        display_df.at[metric, best_ticker] = f"🏆 {display_df.at[metric, best_ticker]}"
                
                st.dataframe(display_df, use_container_width=True, height=650)
