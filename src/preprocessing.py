import pandas as pd
import numpy as np
from scipy.stats import zscore

def preprocess_data(log_entries):
    df = pd.DataFrame(log_entries)
    df["resource"] = df["endpoint"].apply(lambda x: x.split("/")[2] if len(x.split("/")) > 2 else "unknown")
    df["success"] = df["status"] < 400
    df["is_error"] = df["status"] >= 400
    return df

def compute_statistics(df):
    stats = df.groupby("endpoint")["response_time"].agg(["count", "mean", "median", "min", "max", "std"]).dropna()
    stats["p90"] = df.groupby("endpoint")["response_time"].apply(lambda x: np.percentile(x.dropna(), 90))
    stats["p95"] = df.groupby("endpoint")["response_time"].apply(lambda x: np.percentile(x.dropna(), 95))
    return stats

def detect_outliers(df):
    df = df[df["response_time"].notnull()]
    df["zscore"] = zscore(df["response_time"])
    outliers = df[np.abs(df["zscore"]) > 2]
    return outliers
