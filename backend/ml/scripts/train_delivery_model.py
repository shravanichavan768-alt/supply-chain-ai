
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

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "delivery_logistics.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def extract_hours_from_corrupted_timestamp(value: str) -> float:
    
    try:
        nanosecond_part = value.split(".")[-1]
        hours = int(nanosecond_part)
        return float(hours)
    except (ValueError, IndexError):
        return np.nan


def load_and_engineer_features():
    df = pd.read_csv(DATA_PATH)

    # Fix corrupted time columns
    df["delivery_time_hours"] = df["delivery_time_hours"].apply(extract_hours_from_corrupted_timestamp)
    df["expected_time_hours"] = df["expected_time_hours"].apply(extract_hours_from_corrupted_timestamp)

    # Drop rows where time parsing failed, and drop the meaningless id column
    df = df.dropna(subset=["delivery_time_hours", "expected_time_hours"])
    df = df.drop(columns=["delivery_id"])

    # Encode categorical variables
    categorical_cols = [
        "delivery_partner", "package_type", "vehicle_type",
        "delivery_mode", "region", "weather_condition",
    ]
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col])
        encoders[col] = le

    feature_cols = [
        "delivery_partner_enc", "package_type_enc", "vehicle_type_enc",
        "delivery_mode_enc", "region_enc", "weather_condition_enc",
        "distance_km", "package_weight_kg", "expected_time_hours",
    ]

    X = df[feature_cols]
    y = df["delivery_time_hours"]  # predicting actual delivery time

    return X, y, encoders, feature_cols


def evaluate_model(name, model, X_test, y_test):
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    print(f"\n{name}:")
    print(f"  RMSE: {rmse:.2f} hours")
    print(f"  MAE:  {mae:.2f} hours")
    print(f"  R²:   {r2:.4f}")
    return {"name": name, "rmse": rmse, "mae": mae, "r2": r2, "model": model}


def main():
    print("Loading data and engineering features...")
    X, y, encoders, feature_cols = load_and_engineer_features()
    print(f"Final dataset size after cleaning: {len(X)} rows")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    results = []

    print("\nTraining Linear Regression (baseline)...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    results.append(evaluate_model("Linear Regression", lr, X_test, y_test))

    print("\nTraining Random Forest...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    results.append(evaluate_model("Random Forest", rf, X_test, y_test))

    print("\nTraining XGBoost...")
    xgb_model = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
    xgb_model.fit(X_train, y_train)
    results.append(evaluate_model("XGBoost", xgb_model, X_test, y_test))

    best = min(results, key=lambda r: r["rmse"])
    print(f"\n{'='*50}")
    print(f"Best model: {best['name']} (RMSE: {best['rmse']:.2f} hours, R²: {best['r2']:.4f})")
    print(f"{'='*50}")

    model_bundle = {
        "model": best["model"],
        "model_name": best["name"],
        "encoders": encoders,
        "feature_cols": feature_cols,
    }
    save_path = os.path.join(MODEL_DIR, "delivery_time_model.pkl")
    joblib.dump(model_bundle, save_path)
    print(f"\nSaved best model bundle to {save_path}")

    print("\nModel Comparison:")
    print(f"{'Model':<20}{'RMSE':<10}{'MAE':<10}{'R²':<10}")
    for r in results:
        print(f"{r['name']:<20}{r['rmse']:<10.2f}{r['mae']:<10.2f}{r['r2']:<10.4f}")


if __name__ == "__main__":
    main()