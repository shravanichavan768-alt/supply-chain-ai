
import pandas as pd
import numpy as np
import os
import joblib
from datetime import timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "online_retail.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_and_clean_data():
    df = pd.read_csv(DATA_PATH, encoding="ISO-8859-1")

    
    df = df.dropna(subset=["Customer ID"])
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalAmount"] = df["Quantity"] * df["Price"]

    return df


def compute_rfm(df):
    reference_date = df["InvoiceDate"].max() + timedelta(days=1)

    rfm = df.groupby("Customer ID").agg(
        Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
        Frequency=("Invoice", "nunique"),
        Monetary=("TotalAmount", "sum"),
    ).reset_index()

    return rfm


def main():
    print("Loading and cleaning data...")
    df = load_and_clean_data()
    print(f"Cleaned dataset size: {len(df)} rows")

    print("\nComputing RFM metrics per customer...")
    rfm = compute_rfm(df)
    print(f"Number of unique customers: {len(rfm)}")
    print("\nRFM summary statistics:")
    print(rfm[["Recency", "Frequency", "Monetary"]].describe())

    rfm["Frequency_log"] = np.log1p(rfm["Frequency"])
    rfm["Monetary_log"] = np.log1p(rfm["Monetary"])

    features = rfm[["Recency", "Frequency_log", "Monetary_log"]]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

  
    print("\nTraining K-Means (testing k=2 to 6)...")
    best_k = None
    best_score = -1
    best_kmeans_model = None
    for k in range(2, 7):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(scaled_features)
        score = silhouette_score(scaled_features, labels)
        print(f"  k={k}: silhouette score = {score:.4f}")
        if score > best_score:
            best_score = score
            best_k = k
            best_kmeans_model = kmeans

    print(f"\nBest K-Means: k={best_k}, silhouette score={best_score:.4f}")
    rfm["KMeans_Cluster"] = best_kmeans_model.predict(scaled_features)

   
    print("\nTraining DBSCAN...")
    dbscan = DBSCAN(eps=0.5, min_samples=10)
    dbscan_labels = dbscan.fit_predict(scaled_features)
    num_clusters_dbscan = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
    num_noise = list(dbscan_labels).count(-1)
    print(f"  DBSCAN found {num_clusters_dbscan} clusters, {num_noise} noise points")
    rfm["DBSCAN_Cluster"] = dbscan_labels

    
    print("\nK-Means Segment Profiles:")
    segment_summary = rfm.groupby("KMeans_Cluster")[["Recency", "Frequency", "Monetary"]].mean()
    print(segment_summary)

    model_bundle = {
        "kmeans_model": best_kmeans_model,
        "scaler": scaler,
        "best_k": best_k,
        "silhouette_score": best_score,
    }
    save_path = os.path.join(MODEL_DIR, "segmentation_model.pkl")
    joblib.dump(model_bundle, save_path)
    print(f"\nSaved segmentation model to {save_path}")

    
    rfm_output_path = os.path.join(os.path.dirname(__file__), "..", "data", "customer_segments.csv")
    rfm.to_csv(rfm_output_path, index=False)
    print(f"Saved customer segments to {rfm_output_path}")


if __name__ == "__main__":
    main()