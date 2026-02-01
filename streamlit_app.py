import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import kagglehub

# -------------------------------------------------------------------
# Page config
st.set_page_config(
    page_title="📊 Stock Market Dashboard",
    page_icon=":chart_with_upwards_trend:"
)

# -------------------------------------------------------------------
# Load all CSV files from Kaggle dataset
@st.cache_data
def load_data():
    dataset_path = kagglehub.dataset_download("jacksoncrow/stock-market-dataset")
    csv_files = list(Path(dataset_path).rglob("*.csv"))
    if not csv_files:
        st.error("No CSV files found in the dataset")
        return pd.DataFrame()
    
    # Read and concatenate all CSVs
    all_data = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            # Only include files that actually have a Date column
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df["Ticker"] = file.stem  # Use filename (without extension) as ticker
                all_data.append(df)
        except Exception as e:
            # Skip files that fail to load
            continue
    
    if not all_data:
        st.error("No valid stock files with a 'Date' column found.")
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)

df = load_data()

# -------------------------------------------------------------------
# Sidebar filters
if df.empty:
    st.stop()

st.sidebar.header("Filters")

min_date = df["Date"].min()
max_date = df["Date"].max()

date_range = st.sidebar.date_input(
    "Select date range",
    value=[min_date, max_date]
)

tickers = df["Ticker"].unique()
selected_tickers = st.sidebar.multiselect(
    "Select stock ticker(s)",
    tickers,
    default=[tickers[0]] if len(tickers) > 0 else []
)

# -------------------------------------------------------------------
# Filter data
mask = (df["Date"] >= pd.to_datetime(date_range[0])) & (df["Date"] <= pd.to_datetime(date_range[1]))
if selected_tickers:
    mask &= df["Ticker"].isin(selected_tickers)

filtered_df = df[mask]

# -------------------------------------------------------------------
# Dashboard content
st.title("📈 Stock Market Trends Dashboard")

st.write("### Filtered data sample")
st.write(filtered_df.head())

st.write("### Closing Price Over Time")
if "Close" in filtered_df.columns and not filtered_df.empty:
    chart_data = filtered_df.pivot_table(
        index="Date", columns="Ticker", values="Close"
    )
    st.line_chart(chart_data)
else:
    st.warning("No 'Close' prices available to display.")

st.write("### Latest Metrics")
latest_date = filtered_df["Date"].max()
latest_data = filtered_df[filtered_df["Date"] == latest_date]

for ticker in selected_tickers:
    ticker_data = latest_data[latest_data["Ticker"] == ticker]
    if not ticker_data.empty and "Close" in ticker_data.columns:
        last_close = ticker_data["Close"].iloc[-1]
        start_close = filtered_df[(filtered_df["Ticker"] == ticker) & (filtered_df["Date"] == pd.to_datetime(date_range[0]))]["Close"]
        if not start_close.empty:
            change = last_close - start_close.iloc[0]
        else:
            change = 0
        st.metric(
            label=f"{ticker} Close",
            value=f"${last_close:,.2f}",
            delta=f"${change:,.2f}"
        )
    else:
        st.write(f"No Close price data for {ticker}")
