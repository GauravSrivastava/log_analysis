import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

def plot_time_series(df):
    st.subheader("Time Series of Response Times")
    for endpoint in df["endpoint"].unique():
        subset = df[(df["endpoint"] == endpoint) & (df["response_time"].notnull())]
        if not subset.empty:
            fig, ax = plt.subplots()
            ax.plot(subset["timestamp"], subset["response_time"], marker='o')
            ax.set_title(f"Response Time Over Time - {endpoint}")
            ax.set_xlabel("Timestamp")
            ax.set_ylabel("Response Time (ms)")
            st.pyplot(fig)

def plot_error_rate(df):
    st.subheader("Error Rate per Endpoint")
    error_rate = df.groupby("endpoint")["is_error"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots()
    error_rate.plot(kind="bar", ax=ax)
    ax.set_ylabel("Error Rate")
    ax.set_title("Error Rate per Endpoint")
    st.pyplot(fig)

def plot_heatmap(df):
    st.subheader("Heatmap: Endpoint vs Avg Response Time and Error Count")
    heatmap_data = df.groupby("endpoint").agg(
        avg_response_time=("response_time", "mean"),
        error_count=("is_error", "sum")
    )
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax)
    st.pyplot(fig)

def plot_success_failure(df):
    st.subheader("Successful vs Failed Requests")
    success_counts = df.groupby(["endpoint", "success"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots()
    success_counts.plot(kind="bar", stacked=True, ax=ax)
    ax.set_title("Successful vs Failed Requests per Endpoint")
    ax.set_ylabel("Count")
    st.pyplot(fig)

def plot_distribution_plots(df):
    st.subheader("Response Time Distribution Plots")
    for endpoint in df["endpoint"].unique():
        subset = df[(df["endpoint"] == endpoint) & (df["response_time"].notnull())]
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
