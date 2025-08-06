
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
from scipy.stats import zscore

# Load all log files from 'logs' folder
log_entries = []
log_pattern = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z).*?method=(?P<method>\w+).*?endpoint=(?P<endpoint>\S+).*?status=(?P<status>\d+)(?:.*?response_time=(?P<response_time>\d+)ms)?'
)

log_folder = "logs"
for filename in os.listdir(log_folder):
    filepath = os.path.join(log_folder, filename)
    if os.path.isfile(filepath):
        with open(filepath, "r") as file:
            lines = file.readlines()
            for line in lines:
                match = log_pattern.search(line)
                if match:
                    entry = match.groupdict()
                    entry["timestamp"] = datetime.strptime(entry["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                    entry["status"] = int(entry["status"])
                    entry["response_time"] = int(entry["response_time"]) if entry["response_time"] else None
                    log_entries.append(entry)

# Create DataFrame
df = pd.DataFrame(log_entries)

# Streamlit Dashboard
st.title("Endpoint Response Time Analysis Dashboard")

# Filters
endpoints = st.multiselect("Select Endpoints", options=df["endpoint"].unique(), default=df["endpoint"].unique())
methods = st.multiselect("Select Methods", options=df["method"].unique(), default=df["method"].unique())
statuses = st.multiselect("Select Status Codes", options=df["status"].unique(), default=df["status"].unique())

filtered_df = df[df["endpoint"].isin(endpoints) & df["method"].isin(methods) & df["status"].isin(statuses)]

# Time Series Plot
st.subheader("Time Series of Response Times")
for endpoint in filtered_df["endpoint"].unique():
    subset = filtered_df[(filtered_df["endpoint"] == endpoint) & (filtered_df["response_time"].notnull())]
    if not subset.empty:
        fig, ax = plt.subplots()
        ax.plot(subset["timestamp"], subset["response_time"], marker='o')
        ax.set_title(f"Response Time Over Time - {endpoint}")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Response Time (ms)")
        st.pyplot(fig)

# Error Rate Visualization
st.subheader("Error Rate per Endpoint")
error_df = filtered_df.copy()
error_df["is_error"] = error_df["status"] >= 400
error_rate = error_df.groupby("endpoint")["is_error"].mean().sort_values(ascending=False)
fig, ax = plt.subplots()
error_rate.plot(kind="bar", ax=ax)
ax.set_ylabel("Error Rate")
ax.set_title("Error Rate per Endpoint")
st.pyplot(fig)

# Heatmap of Average Response Time and Error Count
st.subheader("Heatmap: Endpoint vs Avg Response Time and Error Count")
heatmap_data = filtered_df.groupby("endpoint").agg(
    avg_response_time=("response_time", "mean"),
    error_count=("status", lambda x: (x >= 400).sum())
)
fig, ax = plt.subplots()
sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax)
st.pyplot(fig)

# Statistical Summary with P90 and P95
st.subheader("Statistical Summary with P90 and P95")
stats = filtered_df.groupby("endpoint")["response_time"].agg(["count", "mean", "median", "min", "max", "std"]).dropna()
stats["p90"] = filtered_df.groupby("endpoint")["response_time"].apply(lambda x: np.percentile(x.dropna(), 90))
stats["p95"] = filtered_df.groupby("endpoint")["response_time"].apply(lambda x: np.percentile(x.dropna(), 95))
st.dataframe(stats)

# Outlier Detection
st.subheader("Outlier Detection")
outlier_df = filtered_df.copy()
outlier_df = outlier_df[outlier_df["response_time"].notnull()]
outlier_df["zscore"] = zscore(outlier_df["response_time"])
outliers = outlier_df[np.abs(outlier_df["zscore"]) > 2]
st.write(f"Detected {len(outliers)} outliers (z-score > 2):")
st.dataframe(outliers[["timestamp", "endpoint", "response_time", "zscore"]])

# Grouping by Resource Type
st.subheader("Grouped Analysis by Resource Type")
def extract_resource(endpoint):
    parts = endpoint.split("/")
    return parts[2] if len(parts) > 2 else "unknown"

filtered_df["resource"] = filtered_df["endpoint"].apply(extract_resource)
grouped_stats = filtered_df.groupby("resource")["response_time"].agg(["count", "mean", "median", "min", "max", "std"]).dropna()
st.dataframe(grouped_stats)

# Successful vs Failed Requests
st.subheader("Successful vs Failed Requests")
filtered_df["success"] = filtered_df["status"] < 400
success_counts = filtered_df.groupby(["endpoint", "success"]).size().unstack(fill_value=0)
fig, ax = plt.subplots()
success_counts.plot(kind="bar", stacked=True, ax=ax)
ax.set_title("Successful vs Failed Requests per Endpoint")
ax.set_ylabel("Count")
st.pyplot(fig)

# Additional Visualizations: Histogram, Violin, Box, Line Plots
st.subheader("Response Time Distribution Plots")
for endpoint in filtered_df["endpoint"].unique():
    subset = filtered_df[(filtered_df["endpoint"] == endpoint) & (filtered_df["response_time"].notnull())]
    if len(subset) >= 2:
        p90 = np.percentile(subset["response_time"], 90)
        p95 = np.percentile(subset["response_time"], 95)

        # Histogram
        fig, ax = plt.subplots()
        sns.histplot(subset["response_time"], kde=True, ax=ax, color='skyblue')
        ax.axvline(p90, color='orange', linestyle='--', label=f'P90: {p90:.2f} ms')
        ax.axvline(p95, color='red', linestyle='--', label=f'P95: {p95:.2f} ms')
        ax.set_title(f"Histogram - {endpoint}")
        ax.set_xlabel("Response Time (ms)")
        ax.legend()
        st.pyplot(fig)

        # Violin Plot
        fig, ax = plt.subplots()
        sns.violinplot(x=subset["response_time"], ax=ax, color='lightgreen')
        ax.axvline(p90, color='orange', linestyle='--', label=f'P90: {p90:.2f} ms')
        ax.axvline(p95, color='red', linestyle='--', label=f'P95: {p95:.2f} ms')
        ax.set_title(f"Violin Plot - {endpoint}")
        ax.set_xlabel("Response Time (ms)")
        ax.legend()
        st.pyplot(fig)

        # Box Plot
        fig, ax = plt.subplots()
        sns.boxplot(x=subset["response_time"], ax=ax, color='lightblue')
        ax.axvline(p90, color='orange', linestyle='--', label=f'P90: {p90:.2f} ms')
        ax.axvline(p95, color='red', linestyle='--', label=f'P95: {p95:.2f} ms')
        ax.set_title(f"Box Plot - {endpoint}")
        ax.set_xlabel("Response Time (ms)")
        ax.legend()
        st.pyplot(fig)

        # Line Plot
        fig, ax = plt.subplots()
        ax.plot(subset["response_time"].values, marker='o', linestyle='-', color='blue', label='Response Time')
        ax.axhline(p90, color='orange', linestyle='--', label=f'P90: {p90:.2f} ms')
        ax.axhline(p95, color='red', linestyle='--', label=f'P95: {p95:.2f} ms')
        ax.set_title(f"Line Plot - {endpoint}")
        ax.set_xlabel("Request Index")
        ax.set_ylabel("Response Time (ms)")
        ax.legend()
        st.pyplot(fig)
