import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import kagglehub

# -------------------------------------------------------------------
# Page configuration
st.set_page_config(
    page_title="📊 Marketing / Stock Dashboard",
    page_icon=":bar_chart:"
)

# -------------------------------------------------------------------
# Download dataset from Kaggle
@st.cache_data
def load_dataset():
    # Download the dataset
    dataset_path = kagglehub.dataset_download("jacksoncrow/stock-market-dataset")
    csv_files = list(Path(dataset_path).rglob("*.csv"))
    if not csv_files:
        st.error("No CSV files found in dataset")
        return pd.DataFrame()
    # Load first CSV
    df = pd.read_csv(csv_files[0])
    # Ensure 'Date' column is datetime
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        st.error("Dataset does not contain 'Date' column")
    # Add Ticker if missing
    if "Ticker" not in df.columns:
        df["Ticker"] = "Stock"
    return df

df = load_dataset()

# -------------------------------------------------------------------
# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
if not df.empty:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    date_range = st.sidebar.date_input(
        "Select date range",
        value=[min_date, max_date]
    )

# Ticker filter
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
# Filter data based on selections
mask = (df["Date"] >= pd.to_datetime(date_range[0])) & (df["Date"] <= pd.to_datetime(date_range[1]))
if selected_tickers:
    mask &= df["Ticker"].isin(selected_tickers)

filtered_df = df[mask]

# -------------------------------------------------------------------
# Page title
st.title("📈 Marketing / Stock Dashboard")

# Show filtered dataset
st.write("### Filtered Data", filtered_df.head())

# -------------------------------------------------------------------
# Line chart of closing prices
st.write("### Closing Prices Over Time")
if "Close" in filtered_df.columns and not filtered_df.empty:
    pivot_chart = filtered_df.pivot_table(index="Date", columns="Ticker", values="Close", aggfunc="mean")
    st.line_chart(pivot_chart)
else:
    st.warning("No 'Close' column or empty data to plot")

# -------------------------------------------------------------------
# Show metrics: latest close and change from start
st.write("### Latest Metrics")
latest_date = filtered_df["Date"].max()
latest_data = filtered_df[filtered_df["Date"] == latest_date]

with st.container():
    for ticker in selected_tickers or ["All Stocks"]:
        if ticker != "All Stocks":
            data_ticker = latest_data[latest_data["Ticker"] == ticker]
            first_data = filtered_df[filtered_df["Ticker"] == ticker]
        else:
            data_ticker = latest_data
            first_data = filtered_df

        if not data_ticker.empty and "Close" in data_ticker.columns:
            last_close = data_ticker["Close"].iloc[-1]
            start_close = first_data[first_data["Date"] == pd.to_datetime(date_range[0])]["Close"].iloc[0]
            change = last_close - start_close
            st.metric(
                label=f"{ticker} Close Price",
                value=f"${last_close:,.2f}",
                delta=f"${change:,.2f}"
            )
        else:
            st.write(f"No data for {ticker}")
