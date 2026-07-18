import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "delivery_logistics.csv")

df = pd.read_csv(DATA_PATH)

print("Shape:", df.shape)
print("\nColumns and dtypes:")
print(df.dtypes)
print("\nFirst 5 rows:")
print(df.head())
print("\nMissing values per column:")
print(df.isnull().sum())

print("\nUnique delivery_id sample:")
print(df["delivery_id"].unique()[:10])

print("\nSample delivery_time_hours values:")
print(df["delivery_time_hours"].unique()[:10])

print("\nSample expected_time_hours values:")
print(df["expected_time_hours"].unique()[:10])

print("\ndelayed value counts:")
print(df["delayed"].value_counts())

print("\ndelivery_status value counts:")
print(df["delivery_status"].value_counts())