import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import kagglehub
from pathlib import Path

# -------------------------------------------------------------------
# Page configuration
st.set_page_config(
    page_title="📈 Stock Market Dashboard",
    page_icon=":chart_with_upwards_trend:"
)

# -------------------------------------------------------------------
# Download dataset from Kaggle
@st.cache_data
def download_dataset():
    # Download the dataset
    path = kagglehub.dataset_download("jacksoncrow/stock-market-dataset")
    # Find CSV files inside
    csv_files = list(Path(path).rglob("*.csv"))
    if csv_files:
        # Use first CSV for simplicity
        return pd.read_csv(csv_files[0])
    else:
        st.error("No CSV files found in dataset")
        return pd.DataFrame()

# Load data
df = download_dataset()

# -------------------------------------------------------------------
# Preprocess dataset
if not df.empty:
    # Ensure Date column is datetime
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        st.error("Dataset does not contain 'Date' column")

    # Check for Ticker column, if not present add a dummy
    if "Ticker" not in df.columns:
        df["Ticker"] = "Stock"

# -------------------------------------------------------------------
# Sidebar filters
st.sidebar.header("Filters")

# Date range
if not df.empty:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    date_range = st.sidebar.date_input(
        "Select date range",
        value=[min_date, max_date]
    )

# Ticker selection
if "Ticker" in df.columns:
    tickers = df["Ticker"].unique()
    selected_tickers = st.sidebar.multiselect(
        "Select stock tickers",
        tickers,
        default=[tickers[0]] if len(tickers) > 0 else []
    )
else:
    selected_tickers = []

# -------------------------------------------------------------------
# Filter data
mask = (df["Date"] >= pd.to_datetime(date_range[0])) & (df["Date"] <= pd.to_datetime(date_range[1]))
if selected_tickers:
    mask &= df["Ticker"].isin(selected_tickers)

filtered_df = df[mask]

# -------------------------------------------------------------------
# Page title
st.title("📊 Stock Market Price Trends")

# Show filtered dataset
st.write("### Filtered data", filtered_df.head())

# -------------------------------------------------------------------
# Closing price line chart
st.write("### 📈 Closing Price Over Time")
if "Close" in filtered_df.columns and not filtered_df.empty:
    pivot_chart = filtered_df.pivot_table(index="Date", columns="Ticker", values="Close", aggfunc="mean")
    st.line_chart(pivot_chart)
else:
    st.warning("No 'Close' column or empty data to plot")

# -------------------------------------------------------------------
# Metrics: latest close and change
st.write("### 📊 Latest Metrics")
latest_date = filtered_df["Date"].max()
latest_data = filtered_df[filtered_df["Date"] == latest_date]

with st.container():
    for ticker in selected_tickers or ["All Stocks"]:
        if ticker != "All Stocks":
            data_ticker = latest_data[latest_data["Ticker"] == ticker]
        else:
            data_ticker = latest_data

        if not data_ticker.empty and "Close" in data_ticker.columns:
            last_close = data_ticker["Close"].iloc[-1]
            first_close = filtered_df[filtered_df["Date"] == pd.to_datetime(date_range[0])]
            if ticker != "All Stocks":
                first_close = first_close[first_close["Ticker"] == ticker]["Close"].iloc[0]
            else:
                first_close = first_close["Close"].iloc[0]
            change = last_close - first_close
            st.metric(
                label=f"{ticker} Close Price",
                value=f"${last_close:,.2f}",
                delta=f"${change:,.2f}"
            )
        else:
            st.write(f"No data for {ticker}")

# -------------------------------------------------------------------
# End of file
