import streamlit as st
import pandas as pd
from pathlib import Path
import kagglehub

# -------------------------------------------------------------------
# Page config
st.set_page_config(page_title="📊 Stock Market Dashboard", page_icon=":chart_with_upwards_trend:")

st.title("📈 Stock Market Trends Dashboard")

# 1. LAZY LOADING: Use a sidebar button to trigger the heavy work
st.sidebar.header("Setup")
load_button = st.sidebar.button("Download & Process Data")

@st.cache_data(show_spinner="Downloading dataset (this may take a while)...")
def load_data():
    # Download once, cache the path
    dataset_path = kagglehub.dataset_download("jacksoncrow/stock-market-dataset")
    
    # REDUCE DATA SIZE: Let's focus only on a specific folder (e.g., 'stocks') 
    # and limit the number of files to prevent memory crashes.
    csv_files = list(Path(dataset_path).rglob("stocks/*.csv"))[:50] # Limit to 50 stocks for speed
    
    all_data = []
    for file in csv_files:
        try:
            # Optimize: only load the columns we actually need
            df = pd.read_csv(file, usecols=["Date", "Close"])
            df["Date"] = pd.to_datetime(df["Date"])
            df["Ticker"] = file.stem
            all_data.append(df)
        except Exception:
            continue
    
    if not all_data:
        return pd.DataFrame()
    return pd.concat(all_data, ignore_index=True)

# Main Logic
if load_button:
    df = load_data()
    st.session_state['df'] = df
    st.success("Data loaded successfully!")

# Check if data exists in session state before proceeding
if 'df' not in st.session_state:
    st.info("👈 Click 'Download & Process Data' in the sidebar to begin.")
    st.stop()

df = st.session_state['df']

# -------------------------------------------------------------------
# Sidebar filters (Same as your original code)
st.sidebar.divider()
st.sidebar.header("Filters")

# ... rest of your filter and metric logic remains the same ...
