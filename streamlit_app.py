import streamlit as st
import pandas as pd

# -------------------------------------------------------------------
# Page configuration
st.set_page_config(
    page_title="📊 Pro Stock Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

# -------------------------------------------------------------------
# Load the pre-processed data
@st.cache_data
def load_data():
    # This reads the small, fast file you uploaded to GitHub
    df = pd.read_parquet("processed_stocks.parquet")
    # Ensure Date is datetime format
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# -------------------------------------------------------------------
# Sidebar - Navigation & Filters
st.sidebar.header("Dashboard Filters")

# Ticker Selection
tickers = sorted(df["Ticker"].unique())
selected_ticker = st.sidebar.selectbox("Select Stock Ticker", tickers)

# Date Range Selection
min_date = df["Date"].min().to_pydatetime()
max_date = df["Date"].max().to_pydatetime()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# -------------------------------------------------------------------
# Filter Logic
# Handle the case where the user hasn't finished selecting a range
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (
        (df["Ticker"] == selected_ticker) & 
        (df["Date"] >= pd.to_datetime(start_date)) & 
        (df["Date"] <= pd.to_datetime(end_date))
    )
    filtered_df = df[mask].sort_values("Date")
else:
    st.info("Please select a start and end date.")
    st.stop()

# -------------------------------------------------------------------
# Main UI
st.title(f"📈 {selected_ticker} Performance Analysis")

if not filtered_df.empty:
    # Top Metrics Row
    col1, col2, col3 = st.columns(3)
    
    current_price = filtered_df["Close"].iloc[-1]
    open_price = filtered_df["Close"].iloc[0]
    price_change = current_price - open_price
    pct_change = (price_change / open_price) * 100

    col1.metric("Current Price", f"${current_price:,.2f}")
    col2.metric("Period Change", f"${price_change:,.2f}", f"{pct_change:.2f}%")
    col3.metric("Data Points", len(filtered_df))

    # Main Chart
    st.subheader("Closing Price Trend")
    st.line_chart(filtered_df.set_index("Date")["Close"])

    # Data Table
    with st.expander("View Raw Data"):
        st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("No data found for the selected criteria.")
