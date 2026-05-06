import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Quantum Terminal", page_icon="🔘", layout="wide")

# 2. Apple Glassmorphism & Titanium CSS
st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617); }
    .header-container {
        padding: 1.2rem; background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(15px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05); border-radius: 0 0 24px 24px;
        margin-bottom: 2rem; position: sticky; top: 0; z-index: 1000;
    }
    html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif !important; }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 15px; border-radius: 12px; backdrop-filter: blur(5px);
    }
    [data-testid="stMetricValue"] { color: #f8fafc !important; font-weight: 700 !important; font-size: 1.6rem !important; }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 0.1em; }
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important; color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 30px !important; text-align: center;
    }
    .stButton>button {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
        color: white !important; border: none !important; border-radius: 30px !important; font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Navigation Header
with st.container():
    st.markdown("<div class='header-container'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: st.markdown("<h3 style='margin:0; color:#f8fafc; font-weight:700; padding-top:8px;'>QUANTUM_OS</h3>", unsafe_allow_html=True)
    with c2: tickers_input = st.text_input("", "MSFT, AAPL, NVDA", label_visibility="collapsed")
    with c3: analyze_button = st.button("SYNC TERMINAL", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Data Engine
@st.cache_data(ttl=3600)
def get_data(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        info = t.info
        if 'shortName' not in info: return None
        bs = t.balance_sheet; is_stmt = t.income_stmt
        total_assets = bs.loc['Total Assets'].iloc[0] if 'Total Assets' in bs.index else 0
        total_liab = bs.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in bs.index else 0
        asset_liab_ratio = total_assets / total_liab if total_liab > 0 else 0
        net_income = is_stmt.loc['Net Income'].iloc[0] if 'Net Income' in is_stmt.index else 0
        total_debt = bs.loc['Total Debt'].iloc[0] if 'Total Debt' in bs.index else 0
        equity = bs.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in bs.index else 0
        roic = net_income / (total_debt + equity) if (total_debt + equity) > 0 else 0
        net_margin = info.get('profitMargins', 0)
        rev = info.get('totalRevenue', 1)
        fcf = info.get('freeCashflow', 0)
        fcf_margin = fcf / rev if rev > 0 else 0
        rev_growth = info.get('revenueGrowth', 0)
        return {
            "P/E Ratio": info.get('trailingPE', 0), "P/S Ratio": info.get('priceToSalesTrailing12Months', 0),
            "Forward P/E": info.get('forwardPE', 0), "Op Margin %": info.get('operatingMargins', 0) * 100,
            "Net Margin %": net_margin * 100, "FCF Margin %": fcf_margin * 100,
            "Current Ratio": info.get('currentRatio', 0), "Debt to Equity": info.get('debtToEquity', 0),
            "Asset/Liab Ratio": asset_liab_ratio, "Price/Book": info.get('priceToBook', 0),
            "Rev Per Share": info.get('revenuePerShare', 0), "EPS": info.get('trailingEps', 0),
            "Rev Growth YoY %": rev_growth * 100, "Rule of 40 %": (fcf_margin + rev_growth) * 100,
            "FNR Percent": (net_margin + fcf_margin + rev_growth) * 100,
            "ROE %": info.get('returnOnEquity', 0) * 100, "ROA %": info.get('returnOnAssets', 0) * 100,
            "ROIC %": roic * 100, "Current Price": info.get('currentPrice', 0)
        }
    except Exception: return None

# 5. UI Logic
tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

if analyze_button or tickers:
    data_dict = {t: get_data(t) for t in tickers if get_data(t)}
    valid_tickers = list(data_dict.keys())
    if not valid_tickers: st.warning("TARGET OFFLINE.")
    
    # SINGLE STOCK: COMPREHENSIVE TEAR SHEET
    elif len(valid_tickers) == 1:
        t = valid_tickers[0]; d = data_dict[t]
        st.markdown(f"<h1 style='margin-bottom:0;'>{t} <span style='font-size:20px; color:#64748b;'>Full Intelligence Profile</span></h1>", unsafe_allow_html=True)
        
        # ROW 1: THE CORE MOAT
        st.write("### 💎 Profitability & Efficiency")
        col1, col2 = st.columns([2, 1])
        with col1:
            m1, m2, m3 = st.columns(3)
            m1.metric("FNR Score", f"{d['FNR Percent']:.2f}%")
            m2.metric("Rule of 40", f"{d['Rule of 40 %']:.2f}%")
            m3.metric("ROIC %", f"{d['ROIC %']:.2f}%")
            m4, m5, m6 = st.columns(3)
            m4.metric("ROE %", f"{d['ROE %']:.2f}%")
            m5.metric("ROA %", f"{d['ROA %']:.2f}%")
            m6.metric("Op Margin %", f"{d['Op Margin %']:.2f}%")
        with col2:
            fig = px.bar(pd.DataFrame({'Metric': ['Net', 'FCF'], 'Value': [d['Net Margin %'], d['FCF Margin %']]}), x='Metric', y='Value', height=200, color_discrete_sequence=['#38bdf8'])
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=20,b=0), xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        # ROW 2: BALANCE SHEET & VALUATION
        st.write("### ⚖️ Solvency & Market Pricing")
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Asset/Liab Ratio", f"{d['Asset/Liab Ratio']:.2f}")
        h2.metric("Current Ratio", f"{d['Current Ratio']:.2f}")
        h3.metric("Debt to Equity", f"{d['Debt to Equity']:.2f}")
        h4.metric("Rev Growth YoY", f"{d['Rev Growth YoY %']:.2f}%")
        
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("P/E Ratio", f"{d['P/E Ratio']:.2f}")
        v2.metric("Forward P/E", f"{d['Forward P/E']:.2f}")
        v3.metric("P/S Ratio", f"{d['P/S Ratio']:.2f}")
        v4.metric("Price/Book", f"{d['Price/Book']:.2f}")

        # ROW 3: PER SHARE DATA
        st.write("### 💵 Per Share Intelligence")
        s1, s2, s3 = st.columns(3)
        s1.metric("Current Price", f"${d['Current Price']:.2f}")
        s2.metric("EPS", f"{d['EPS']:.2f}")
        s3.metric("Rev Per Share", f"{d['Rev Per Share']:.2f}")

    # MULTI STOCK: COMPARISON MATRIX
    else:
        df = pd.DataFrame(data_dict)
        st.write("### 📊 Benchmarking Visuals")
        v1, v2 = st.columns(2)
        with v1:
            fig1 = px.bar(x=df.columns, y=df.loc["FNR Percent"], title="FNR Showdown", height=250, color_discrete_sequence=['#38bdf8'])
            fig1.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=40,b=0), xaxis_title="")
            st.plotly_chart(fig1, use_container_width=True)
        with v2:
            fig2 = px.bar(x=df.columns, y=df.loc["Asset/Liab Ratio"], title="Solvency Ratio", height=250, color_discrete_sequence=['#0284c7'])
            fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=40,b=0), xaxis_title="")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<h2 style='color:#f8fafc;'>Fleet Comparison Matrix</h2>", unsafe_allow_html=True)
        display_df = df.apply(lambda x: x.map(lambda y: f"{y:.2f}"))
        max_metrics = ["Op Margin %", "Net Margin %", "FCF Margin %", "Asset/Liab Ratio", "Rev Growth YoY %", "FNR Percent", "ROIC %", "ROE %", "ROA %", "Rev Per Share", "EPS"]
        min_metrics = ["P/E Ratio", "P/S Ratio", "Forward P/E", "Debt to Equity", "Price/Book"]
        for metric in df.index:
            row_data = df.loc[metric]
            if metric in max_metrics: bt = row_data.idxmax()
            elif metric in min_metrics: bt = row_data.idxmin()
            else: continue
            if bt and pd.notna(row_data[bt]): display_df.at[metric, bt] = f"🏆 {display_df.at[metric, bt]}"
        st.dataframe(display_df, use_container_width=True, height=600)
