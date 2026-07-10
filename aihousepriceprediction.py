import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
# --- NEW IMPORTS FOR EVALUATION ---
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. IMPORT DATASET
try:
    df = pd.read_csv('tamilnadu_house_data.csv')
    print("Dataset imported successfully!")
except FileNotFoundError:
    print("Error: tamilnadu_house_data.csv not found.")
    exit()

# 2. PREPROCESSING
categorical_cols = ['City', 'Neighborhood', 'Pincode', 'Nearby Amenities', 'Market Trends']
numerical_cols = ['Property Size (sqft)', 'Lot Size', 'Bedrooms', 'Bathrooms', 'Year Built']

for col in categorical_cols:
    df[col] = df[col].astype(str).str.strip().str.lower()

X = df.drop('Sale Price', axis=1)
y = df['Sale Price']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ])

# 3. TRAINING
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model_pipeline.fit(X_train, y_train)

# ==========================================
# 4. MODEL EVALUATION (NEW SECTION)
# ==========================================
# Predict on the test set to compare with actual prices
y_pred = model_pipeline.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("\n--- Model Performance Metrics ---")
print(f"Mean Absolute Error (MAE): ₹{mae:,.2f}")
print(f"Mean Squared Error (MSE): {mse:,.2f}")
print(f"Root Mean Squared Error (RMSE): ₹{rmse:,.2f}")
print(f"R² Score (Accuracy): {r2:.4f} ({r2*100:.2f}%)")
print("---------------------------------\n")

# ==========================================
# 5. USER INPUT PREDICTION
# ==========================================
def get_user_prediction():
    user_data = {
        'City': input("City: ").lower(),
        'Neighborhood': input("Neighborhood: ").lower(),
        'Pincode': input("Pincode: ").lower(),
        'Property Size (sqft)': float(input("Property Size: ")),
        'Lot Size ': float(input("Lot Size (sqft): ")),
        'Bedrooms': int(input("Bedrooms: ")),
        'Bathrooms': int(input("Bathrooms: ")),
        'Year Built': int(input("Year Built: ")),
        'Nearby Amenities': input("Amenities: ").lower(),
        'Market Trends': input("Market Trend (Declining/Stable/Rising): ").lower()
    }
    prediction = model_pipeline.predict(pd.DataFrame([user_data]))
    print(f"\n Predicted Sale Price: ₹{prediction[0]:,.2f}")

get_user_prediction()