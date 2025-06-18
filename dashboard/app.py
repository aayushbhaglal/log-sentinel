import streamlit as st
import pandas as pd
import time
import os

# Path to drift log CSV
DRIFT_LOG_PATH = "../data/processed/drift_history.csv"

# Page setup
st.set_page_config(page_title="Drift Monitor", layout="wide")
st.title("📈 Log Drift Score Monitoring")

# Container for seamless refresh
placeholder = st.empty()

while True:
    with placeholder.container():
        # Read the latest drift log
        if not os.path.exists(DRIFT_LOG_PATH):
            st.warning("Drift log file not found.")
            time.sleep(3)
            continue

        df = pd.read_csv(DRIFT_LOG_PATH)

        if df.empty:
            st.warning("Drift log file is empty.")
        else:
            st.subheader("📊 Drift Score Over Time")

            # Use timestamp or fallback to line number
            if "start_timestamp" in df.columns and df["start_timestamp"].notna().all():
                df["x"] = pd.to_datetime(df["start_timestamp"])
            else:
                df["x"] = df["start_line"]

            # Show line chart
            st.line_chart(df.set_index("x")[["drift_score"]])

            # Show last few records
            st.subheader("📄 Recent Drift Records")
            st.dataframe(df.tail(10), use_container_width=True)

    time.sleep(3)