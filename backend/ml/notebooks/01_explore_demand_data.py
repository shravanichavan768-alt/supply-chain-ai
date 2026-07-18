import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "demand_forecasting.csv")

df = pd.read_csv(DATA_PATH)

print("Shape:", df.shape)
print("\nColumns and dtypes:")
print(df.dtypes)
print("\nFirst 5 rows:")
print(df.head())
print("\nMissing values per column:")
print(df.isnull().sum())
print("\nDate range:")
print(df["Date"].min(), "to", df["Date"].max())
print("\nUnique stores:", df["Store ID"].nunique())
print("Unique products:", df["Product ID"].nunique())
print("\nDemand stats:")
print(df["Demand"].describe())