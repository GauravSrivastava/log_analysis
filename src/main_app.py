import streamlit as st
from data_loader import load_logs
from preprocessing import preprocess_data, compute_statistics, detect_outliers
from visualizations import (
    plot_time_series, plot_error_rate, plot_heatmap,
    plot_success_failure, plot_distribution_plots
)

# Load and preprocess data
log_entries = load_logs()
df = preprocess_data(log_entries)

# Dashboard layout
st.title("Endpoint Response Time Analysis Dashboard")

# Filters
endpoints = st.multiselect("Select Endpoints", options=df["endpoint"].unique(), default=df["endpoint"].unique())
methods = st.multiselect("Select Methods", options=df["method"].unique(), default=df["method"].unique())
statuses = st.multiselect("Select Status Codes", options=df["status"].unique(), default=df["status"].unique())

filtered_df = df[df["endpoint"].isin(endpoints) & df["method"].isin(methods) & df["status"].isin(statuses)]

# Visualizations
plot_time_series(filtered_df)
plot_error_rate(filtered_df)
plot_heatmap(filtered_df)

# Statistical Summary
st.subheader("Statistical Summary with P90 and P95")
stats = compute_statistics(filtered_df)
st.dataframe(stats)

# Outlier Detection
st.subheader("Outlier Detection")
outliers = detect_outliers(filtered_df)
st.write(f"Detected {len(outliers)} outliers (z-score > 2):")
st.dataframe(outliers[["timestamp", "endpoint", "response_time", "zscore"]])

# Grouped Analysis
st.subheader("Grouped Analysis by Resource Type")
grouped_stats = filtered_df.groupby("resource")["response_time"].agg(["count", "mean", "median", "min", "max", "std"]).dropna()
st.dataframe(grouped_stats)

# Success vs Failure
plot_success_failure(filtered_df)

# Distribution Plots
plot_distribution_plots(filtered_df)
