import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
import mplcursors
import time
import os
import numpy as np
import json

from scripts.config import get_config
from scripts.paths import PROJECT_ROOT

config = get_config()

# Path to drift log CSV
DRIFT_LOG_PATH = str(PROJECT_ROOT / config["drift_history_file_path"])
HEALTH_LOG_PATH = str(PROJECT_ROOT / config["health_logs_path"])

# Page setup
st.set_page_config(page_title="Drift Monitor", layout="wide")
st.title("📈 Log Drift Score Monitoring")

# Container for seamless refresh
placeholder = st.empty()

def color_segments(x, y, labels):
    """Create colored line segments based on labels."""
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    colors = []
    for i in range(len(labels) - 1):
        if labels[i + 1] == "updated":
            colors.append("#2ecc71")  # Green
        elif labels[i + 1] == "alert":
            colors.append("#e74c3c")  # Red
        else:
            colors.append("#3498db")  # Blue

    lc = mcoll.LineCollection(segments, colors=colors, linewidths=2)
    return lc

sidebar_placeholder = st.sidebar.empty()

# Main loop
while True:
    with placeholder.container():
        with sidebar_placeholder.container():
            st.header("🩺 Health Status")
            if os.path.exists(HEALTH_LOG_PATH):
                try:
                    with open(HEALTH_LOG_PATH, "r") as f:
                        health_data = json.load(f)
                    for component, data in health_data.items():
                        timestamp = round(data["timestamp"], 2) if data["timestamp"] else "N/A"
                        st.markdown(f"**{component}**: `{data['status']}` (updated: {timestamp})")
                except Exception as e:
                    st.error("Failed to load health data.")
            else:
                st.info("No health data available yet.")

        if not os.path.exists(DRIFT_LOG_PATH):
            st.warning("Drift log file not found.")
            time.sleep(3)
            continue

        df = pd.read_csv(DRIFT_LOG_PATH)

        if df.empty:
            st.warning("Drift log file is empty.")
        else:
            st.subheader("📊 Drift Score Over Time")

            # x-axis: log line numbers
            x_vals = df["start_line"].values
            y_vals = df["drift_score"].values
            timestamps = df["start_timestamp"].fillna("").values

            # Label rows for segment coloring
            def label_row(row):
                if row["centroid_updated"]:
                    return "updated"
                elif row["alert"]:
                    return "alert"
                else:
                    return "normal"

            df["label"] = df.apply(label_row, axis=1)
            labels = df["label"].values

            # Plot setup
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_alpha(0.0)  # Transparent figure background
            ax.set_facecolor("none")  # Transparent axes

            # Colored segments
            lc = color_segments(x_vals, y_vals, labels)
            ax.add_collection(lc)
            # Show last N points
            visible_points = 50  # Change as needed
            if len(x_vals) > visible_points:
                ax.set_xlim(x_vals[-visible_points], x_vals[-1])
            else:
                ax.set_xlim(x_vals.min(), x_vals.max())
            ax.set_ylim(0, 1)  

            # Threshold line
            ax.axhline(config["drift_threshold"], color='#7f8c8d', linestyle='--', linewidth=1.2, label="Threshold")

            # Axes styling
            ax.tick_params(colors='white', labelsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_xlabel("Log Line Number", fontsize=11, color='white')
            ax.set_ylabel("Drift Score", fontsize=11, color='white')
            ax.set_title("Drift Score Trend", fontsize=13, weight='bold', color='white')
            ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.3)

            # Legend
            custom_lines = [
                plt.Line2D([0], [0], color="#3498db", lw=2, label="Normal"),
                plt.Line2D([0], [0], color="#e74c3c", lw=2, label="Alert"),
                plt.Line2D([0], [0], color="#2ecc71", lw=2, label="Centroid Updated"),
                plt.Line2D([0], [0], color="#7f8c8d", lw=1.2, linestyle='--', label="Threshold"),
            ]
            ax.legend(handles=custom_lines, loc='upper right', fontsize=9)

            # Hover annotations
            cursor = mplcursors.cursor(ax, hover=True)
            @cursor.connect("add")
            def on_add(sel):
                i = sel.index
                timestamp = timestamps[i] if i < len(timestamps) else "N/A"
                drift = y_vals[i] if i < len(y_vals) else "N/A"
                line = x_vals[i] if i < len(x_vals) else "N/A"
                sel.annotation.set_text(f"Line: {line}\nTime: {timestamp}\nDrift: {drift:.4f}")

            # Show plot
            st.pyplot(fig)

            # Show recent drift logs
            st.subheader("📄 Recent Drift Records")

            # Rename columns for display
            display_df = df.tail(10).rename(columns={
                "start_line": "window Start",
                "end_line": "Window End",
                "start_timestamp": "Start Time",
                "end_timestamp": "End Time",
                "drift_score": "Drift Score",
                "centroid_updated": "Centroid Updated",
                "alert": "Alert Triggered",
                "label": "Label"
            })

            st.dataframe(display_df, use_container_width=True)

            fig.tight_layout()

    time.sleep(3)