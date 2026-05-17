import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
from sklearn.metrics import mean_absolute_error

# --- 1. LOAD DATA ---
df = pd.read_csv('data/women_travel_safety_dataset_updated.csv')

# --- 2. FEATURES & TARGET ---
# Ensure columns match the corrected prediction order:
features_order = [
    'travel_hour', 'is_night', 'is_weekend', 'street_lighting', 'road_type_score',
    'nearby_shops', 'police_distance', 'hospital_distance', 'emergency_count',
    'poi_count', 'bus_stop_count', 'commercial_density'
]

X = df[features_order]
y = df['safety_probability']

# --- 3. CREATE CATEGORICAL TARGET FOR LOGISTIC REGRESSION ---
def categorize_safety(p):
    if p < 40: return 0    # Unsafe
    if p < 70: return 1    # Cautious
    return 2               # Safe

y_class = y.apply(categorize_safety)

# --- 4. SPLIT DATA ---
X_train, X_test, y_train, y_test, yc_train, yc_test = train_test_split(
    X, y, y_class, test_size=0.2, random_state=42
)

# --- 5. TRAIN GRADIENT BOOSTING REGRESSOR ---
gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
gb_model.fit(X_train, y_train)

# --- 6. TRAIN LOGISTIC REGRESSION WITH SCALING ---
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

log_model = LogisticRegression(max_iter=1000)
log_model.fit(X_train_scaled, yc_train)

# --- 7. SAVE MODELS & SCALER ---
joblib.dump(gb_model, 'gradient_boosting_model.pkl')
joblib.dump(log_model, 'logistic_regression_model.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("✅ Models and scaler trained & saved successfully!")

# --- 8. EVALUATE MODELS ---
# Gradient Boosting (MAE)
gb_preds = gb_model.predict(X_test)
mae = mean_absolute_error(y_test, gb_preds)

# Logistic Regression (Accuracy)
X_test_scaled = scaler.transform(X_test)
log_accuracy = log_model.score(X_test_scaled, yc_test)

print("\n--- PROJECT METRICS ---")
print(f"Gradient Boosting MAE: {mae:.2f}% (Lower is better)")
print(f"Logistic Regression Accuracy: {log_accuracy * 100:.2f}% (Higher is better)")
