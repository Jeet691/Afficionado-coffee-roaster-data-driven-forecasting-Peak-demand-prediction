import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64

ROOT = Path(__file__).parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

st.set_page_config(page_title="Afficionado Coffee Roasters | Analytics Portfolio",
                   page_icon="☕", layout="wide", initial_sidebar_state="expanded")

# Warm coffee palette
BG = "#201815"
PANEL = "#A94F2B"
ACCENT = "#E9865A"
CREAM = "#F7F0E6"
INK = "#2B211D"
MUTED = "#D8B8A3"

st.markdown(f"""
<style>
.stApp {{ background: {BG}; color: {CREAM}; }}
[data-testid="stSidebar"] {{ background: #2B211D; border-right: 1px solid #69402E; }}
h1,h2,h3 {{ color: {CREAM} !important; }}
p, label, .stMarkdown {{ color: {CREAM}; }}
div[data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid #E6B99B;
 border-radius: 10px; padding: 16px 18px; box-shadow: 0 6px 14px #0005; }}
div[data-testid="stMetricLabel"] p {{ color: #FCE8D8 !important; }}
div[data-testid="stMetricValue"] {{ color: white !important; }}
.block-container {{ padding-top: 1.4rem; }}
section[data-testid="stSidebar"] .stRadio label {{ color: {CREAM}; }}
a {{ color: {ACCENT} !important; }}
.hero {{ background: linear-gradient(110deg,#6E321F,#A94F2B); padding: 2.1rem;
 border-radius: 14px; border: 1px solid #DDA17E; }}
.hero h1 {{ font-size: 2.5rem; margin-bottom: .35rem; }}
.hero p {{ font-size: 1.1rem; color: #FFF0E5; }}
.small-note {{ color: #DCC4B5; font-size: .9rem; }}
</style>
""", unsafe_allow_html=True)

def load_csv(name):
    return pd.read_csv(DATA / name)

@st.cache_data
def datasets():
    tx = load_csv("transactions_clean.csv")
    stores = load_csv("store_summary.csv")
    peaks = load_csv("peak_hours.csv")
    hourly = load_csv("hourly_store_demand.csv")
    cats = load_csv("category_summary.csv")
    tx["transaction_datetime"] = pd.to_datetime(tx["transaction_datetime"], errors="coerce")
    for c in ["hour", "minute", "transaction_qty", "unit_price", "revenue"]:
        if c in tx:
            tx[c] = pd.to_numeric(tx[c], errors="coerce")
    return tx, stores, peaks, hourly, cats

tx, stores, peaks, hourly, cats = datasets()
nav = st.sidebar.radio("PROJECT NAVIGATION", [
    "Home", "Executive Overview", "Peak Demand & Operations",
    "Product & Store Analysis", "Hourly Demand Planning",
    "EDA Report & Resources"
])
st.sidebar.markdown("---")
st.sidebar.caption("Afficionado Coffee Roasters • Data analytics portfolio")
st.sidebar.caption("Built with Streamlit and Plotly")

def metric_row(df):
    revenue = float(df["revenue"].sum()) if len(df) else 0
    qty = float(df["transaction_qty"].sum()) if len(df) else 0
    count = int(df["transaction_id"].nunique()) if len(df) else 0
    atv = revenue / count if count else 0
    a,b,c,d = st.columns(4)
    a.metric("Total Revenue", f"${revenue:,.2f}")
    b.metric("Total Quantity", f"{qty:,.0f}")
    c.metric("Transactions", f"{count:,}")
    d.metric("Avg. Transaction Value", f"${atv:,.2f}")

def filter_tx():
    f1, f2, f3 = st.columns(3)
    locations = ["All stores"] + sorted(tx["store_location"].dropna().unique().tolist())
    categories = ["All categories"] + sorted(tx["product_category"].dropna().unique().tolist())
    dayparts = ["All dayparts"] + sorted(tx["daypart"].dropna().unique().tolist())
    store = f1.selectbox("Store", locations, key=nav+"_store")
    category = f2.selectbox("Product category", categories, key=nav+"_category")
    daypart = f3.selectbox("Daypart", dayparts, key=nav+"_daypart")
    d = tx.copy()
    if store != "All stores": d = d[d.store_location == store]
    if category != "All categories": d = d[d.product_category == category]
    if daypart != "All dayparts": d = d[d.daypart == daypart]
    return d

def chart_style(fig, height=370):
    fig.update_layout(height=height, paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font_color=CREAM, margin=dict(l=25,r=20,t=55,b=30),
        legend=dict(font=dict(color=CREAM)))
    fig.update_xaxes(gridcolor="#D7A88E", zerolinecolor="#D7A88E")
    fig.update_yaxes(gridcolor="#D7A88E", zerolinecolor="#D7A88E")
    return fig

if nav == "Home":
    st.markdown("""<div class="hero"><h1>☕ AFFICIOnADO COFFEE ROASTERS</h1>
    <p>Data-driven forecasting, demand patterns & business insights</p>
    <p class="small-note">An interactive analytics portfolio exploring sales performance, store operations,
    product contribution and intraday demand planning.</p></div>""", unsafe_allow_html=True)
    st.write("")
    st.image(str(ASSETS / "home_afficionado.png"), use_container_width=True)
    metric_row(tx)
    st.subheader("Explore the project")
    cols = st.columns(3)
    for col, title, desc in zip(cols,
        ["Understand performance", "Find peak periods", "Plan with evidence"],
        ["Track revenue, transactions and store results.",
         "Compare hourly volume and identify high-demand windows.",
         "Review observed hourly patterns and model context."]):
        with col:
            st.markdown(f"### {title}")
            st.write(desc)
    st.info("Use the navigation menu to explore the interactive pages, report, notebook, cleaned data and Power BI file.")

elif nav == "Executive Overview":
    st.title("Executive Overview")
    st.caption("Filter the transaction-level dataset and explore core business KPIs.")
    d = filter_tx()
    metric_row(d)
    c1,c2 = st.columns(2)
    with c1:
        by_store = d.groupby("store_location", as_index=False).agg(revenue=("revenue","sum"))
        st.plotly_chart(chart_style(px.bar(by_store, x="store_location", y="revenue",
            title="Revenue by Store", color="store_location", text_auto=".2s")), use_container_width=True)
    with c2:
        by_cat = d.groupby("product_category", as_index=False).agg(revenue=("revenue","sum")).sort_values("revenue",ascending=True)
        st.plotly_chart(chart_style(px.bar(by_cat, x="revenue", y="product_category", orientation="h",
            title="Revenue by Product Category", color="revenue", color_continuous_scale=["#E9865A","#6E321F"])), use_container_width=True)
    st.subheader("Store performance")
    table = d.groupby("store_location", as_index=False).agg(
        transactions=("transaction_id","nunique"), quantity=("transaction_qty","sum"), revenue=("revenue","sum"))
    table["avg_transaction_value"] = table["revenue"] / table["transactions"]
    st.dataframe(table.style.format({"revenue":"${:,.2f}","avg_transaction_value":"${:,.2f}"}), use_container_width=True, hide_index=True)

elif nav == "Peak Demand & Operations":
    st.title("Peak Demand & Operations")
    st.caption("Compare store-level demand by hour and inspect the peak-hour records.")
    d = filter_tx()
    h = d.groupby(["store_location","hour"], as_index=False).agg(quantity=("transaction_qty","sum"), revenue=("revenue","sum"))
    c1,c2 = st.columns(2)
    with c1:
        fig = px.line(h, x="hour", y="quantity", color="store_location", markers=True, title="Hourly Quantity by Store")
        st.plotly_chart(chart_style(fig), use_container_width=True)
    with c2:
        fig = px.bar(h, x="hour", y="quantity", color="store_location", barmode="group", title="Hourly Demand Comparison")
        st.plotly_chart(chart_style(fig), use_container_width=True)
    st.subheader("Peak-hour reference table")
    p = peaks.copy()
    if "store_location" in p:
        chosen = st.multiselect("Stores in peak table", sorted(p.store_location.unique()), default=sorted(p.store_location.unique()))
        p = p[p.store_location.isin(chosen)]
    st.dataframe(p, use_container_width=True, hide_index=True)
    st.info("The EDA defines store-specific peak hours using the 75th percentile of hourly quantity. Interpret the peak table as observed intraday demand, not calendar-seasonality analysis.")

elif nav == "Product & Store Analysis":
    st.title("Product & Store Analysis")
    d = filter_tx()
    c1,c2 = st.columns(2)
    cat = d.groupby("product_category", as_index=False).agg(quantity=("transaction_qty","sum"), revenue=("revenue","sum"))
    with c1:
        fig = px.treemap(cat, path=["product_category"], values="revenue", title="Revenue Contribution by Product Category",
                         color="revenue", color_continuous_scale=["#E9865A","#6E321F"])
        st.plotly_chart(chart_style(fig, 420), use_container_width=True)
    with c2:
        fig = px.scatter(cat, x="quantity", y="revenue", size="revenue", color="product_category",
                         hover_name="product_category", title="Category Performance: Quantity vs Revenue")
        st.plotly_chart(chart_style(fig, 420), use_container_width=True)
    st.subheader("Category detail")
    cat["revenue_share_pct"] = cat["revenue"] / cat["revenue"].sum() * 100 if cat["revenue"].sum() else 0
    st.dataframe(cat.sort_values("revenue",ascending=False).style.format({"revenue":"${:,.2f}","revenue_share_pct":"{:.2f}%"}),
                 use_container_width=True, hide_index=True)
    st.subheader("Store comparison")
    st.dataframe(d.groupby("store_location",as_index=False).agg(
        transactions=("transaction_id","nunique"), quantity=("transaction_qty","sum"),
        revenue=("revenue","sum"), average_unit_price=("unit_price","mean")),
        use_container_width=True, hide_index=True)

elif nav == "Hourly Demand Planning":
    st.title("Hourly Demand Planning")
    st.caption("Observed intraday demand patterns and planning context.")
    d = filter_tx()
    h = d.groupby("hour", as_index=False).agg(quantity=("transaction_qty","sum"), revenue=("revenue","sum"),
                                              transactions=("transaction_id","nunique"))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=h.hour, y=h.quantity, name="Observed quantity", marker_color=ACCENT))
    fig.update_layout(title="Observed Quantity by Hour", xaxis_title="Hour of day", yaxis_title="Quantity")
    st.plotly_chart(chart_style(fig, 420), use_container_width=True)
    fig = px.line(h, x="hour", y=["quantity","transactions"], markers=True, title="Hourly Quantity & Transaction Pattern")
    st.plotly_chart(chart_style(fig, 360), use_container_width=True)
    st.subheader("Hourly summary")
    st.dataframe(h, use_container_width=True, hide_index=True)
    st.warning("Forecasting caveat: the supplied source does not contain a genuine calendar date. The constructed timestamp supports intraday/hourly planning, but daily or weekly forecasts and seasonality are not validated by this dataset.")
    st.markdown("**Planning use:** review store-specific morning demand, prepare Coffee and Tea inventory ahead of busy hours, and evaluate staffing against observed hourly volume.")

else:
    st.title("EDA Report & Project Resources")
    st.write("Review the original analysis and download the project artifacts.")
    pdf_path = ASSETS / "Afficionado_Coffee_Roasters_EDA_Business_Insights_Report.pdf"
    pdf_bytes = pdf_path.read_bytes()
    st.download_button("⬇ Download EDA Business Insights Report (PDF)", pdf_bytes,
                       file_name=pdf_path.name, mime="application/pdf")
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    st.markdown(f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="720" type="application/pdf"></iframe>',
                unsafe_allow_html=True)
    st.subheader("Dashboard screenshots")
    for label, fname in [
        ("Exclusive Overview","exclusive_overview.png"),
        ("Peak Demand & Operations","peak_demand_operations.png"),
        ("Product & Store Analysis","product_store_analysis.png"),
        ("Hourly Demand Forecast & Planning","hourly_demand_forecast_planning.png")]:
        with st.expander(label):
            st.image(str(ASSETS / fname), use_container_width=True)
    st.subheader("Download source files")
    resources = [
        ("Cleaned transaction data","data/transactions_clean.csv","text/csv"),
        ("Store summary","data/store_summary.csv","text/csv"),
        ("Peak-hour data","data/peak_hours.csv","text/csv"),
        ("Hourly store demand","data/hourly_store_demand.csv","text/csv"),
        ("Category summary","data/category_summary.csv","text/csv"),
        ("Python notebook","assets/Afficionado_Coffee_Roasters_notebook.ipynb","application/x-ipynb+json"),
        ("Power BI report","assets/Afficionado_Coffee_Roasters.pbix","application/octet-stream"),
    ]
    for label, rel, mime in resources:
        path = ROOT / rel
        st.download_button(f"Download {label}", path.read_bytes(), file_name=path.name, mime=mime, key=rel)
    st.caption("The Power BI file is included for download; the interactive web charts are rendered natively in Streamlit.")
