import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "online_retail.csv")

df = pd.read_csv(DATA_PATH, encoding="ISO-8859-1")

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())
print("\nMissing values:")
print(df.isnull().sum())
print("\nNegative Quantity count (likely returns):", (df["Quantity"] < 0).sum())
print("Negative Price count:", (df["Price"] < 0).sum())
print("\nCustomer ID missing:", df["Customer ID"].isnull().sum())
print("\nDate range:")
print(df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())