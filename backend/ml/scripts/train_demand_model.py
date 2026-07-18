
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "demand_forecasting.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_and_engineer_features():
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    df["day_of_week"] = df["Date"].dt.dayofweek
    df["month"] = df["Date"].dt.month
    df["day_of_year"] = df["Date"].dt.dayofyear
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    
    df["price_diff_vs_competitor"] = df["Price"] - df["Competitor Pricing"]
    df["discount_pct"] = df["Discount"] / (df["Price"] + 1e-5)  # avoid div-by-zero

   
    categorical_cols = ["Store ID", "Product ID", "Category", "Region", "Weather Condition", "Seasonality"]
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col])
        encoders[col] = le

    feature_cols = [
        "Store ID_enc", "Product ID_enc", "Category_enc", "Region_enc",
        "Inventory Level", "Price", "Discount", "Weather Condition_enc",
        "Promotion", "Competitor Pricing", "Seasonality_enc", "Epidemic",
        "day_of_week", "month", "day_of_year", "is_weekend",
        "price_diff_vs_competitor", "discount_pct",
    ]

    X = df[feature_cols]
    y = df["Demand"]

    return X, y, encoders, feature_cols


def evaluate_model(name, model, X_test, y_test):
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    print(f"\n{name}:")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  MAE:  {mae:.2f}")
    print(f"  R²:   {r2:.4f}")
    return {"name": name, "rmse": rmse, "mae": mae, "r2": r2, "model": model}


def main():
    print("Loading data and engineering features...")
    X, y, encoders, feature_cols = load_and_engineer_features()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    results = []

    print("\nTraining Linear Regression (baseline)...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    results.append(evaluate_model("Linear Regression", lr, X_test, y_test))

    print("\nTraining Random Forest...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    results.append(evaluate_model("Random Forest", rf, X_test, y_test))

    print("\nTraining XGBoost...")
    xgb_model = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
    xgb_model.fit(X_train, y_train)
    results.append(evaluate_model("XGBoost", xgb_model, X_test, y_test))

    print("\nTraining LightGBM...")
    lgb_model = lgb.LGBMRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
    lgb_model.fit(X_train, y_train)
    results.append(evaluate_model("LightGBM", lgb_model, X_test, y_test))

    best = min(results, key=lambda r: r["rmse"])
    print(f"\n{'='*50}")
    print(f"Best model: {best['name']} (RMSE: {best['rmse']:.2f}, R²: {best['r2']:.4f})")
    print(f"{'='*50}")

   
    model_bundle = {
        "model": best["model"],
        "model_name": best["name"],
        "encoders": encoders,
        "feature_cols": feature_cols,
    }
    save_path = os.path.join(MODEL_DIR, "demand_forecast_model.pkl")
    joblib.dump(model_bundle, save_path)
    print(f"\nSaved best model bundle to {save_path}")

    
    print("\nModel Comparison:")
    print(f"{'Model':<20}{'RMSE':<10}{'MAE':<10}{'R²':<10}")
    for r in results:
        print(f"{r['name']:<20}{r['rmse']:<10.2f}{r['mae']:<10.2f}{r['r2']:<10.4f}")


if __name__ == "__main__":
    main()