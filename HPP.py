import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# ==========================================
# 1. IMPORTING THE DATASET
# ==========================================
# Ensure your file is named 'tamilnadu_house_data.csv' and is in the same folder as this script
try:
    df = pd.read_csv('tamilnadu_house_data.csv')
    print("Dataset successfully imported!")
except FileNotFoundError:
    print("Error: 'tamilnadu_house_data.csv' not found. Please check the file name.")
    exit()

# ==========================================
# 2. PREPROCESSING & CASE INSENSITIVITY
# ==========================================
# Columns to handle for case-sensitivity (lowercase conversion)
categorical_cols = ['City', 'Neighborhood', 'Pincode', 'Nearby Amenities', 'Market Trends']
numerical_cols = ['Property Size (sqft)', 'Lot Size', 'Bedrooms', 'Bathrooms', 'Year Built']

# Convert text columns to lowercase to handle inputs like "CHENNAI" or "chennai"
for col in categorical_cols:
    df[col] = df[col].astype(str).str.strip().str.lower()

# Define Features (X) and Target (y)
X = df.drop('Sale Price', axis=1)
y = df['Sale Price']

# Setup Transformers
# - StandardScaler: Normalizes numbers so 'Year Built' doesn't outweigh 'Bedrooms'
# - OneHotEncoder: Converts city/neighborhood names into numbers the AI understands
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ])

# ==========================================
# 3. MODEL ARCHITECTURE & TRAINING
# ==========================================
# Creating a Pipeline ensures user input is processed exactly like the training data
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

# Splitting data for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Training the model
model_pipeline.fit(X_train, y_train)
print(f"Model Training Complete. Accuracy (R2 Score): {model_pipeline.score(X_test, y_test):.2f}")

# ==========================================
# 4. USER INPUT PREDICTION
# ==========================================
print("\n--- Enter Details for Prediction ---")

def get_user_prediction():
    # Accepting user input and immediately lowercasing it for case-insensitivity
    user_data = {
        'City': input("City: ").strip().lower(),
        'Neighborhood': input("Neighborhood: ").strip().lower(),
        'Pincode': input("Pincode: ").strip().lower(),
        'Property Size (sqft)': float(input("Property Size (sqft): ")),
        'Lot Size': float(input("Lot Size: ")),
        'Bedrooms': int(input("Bedrooms: ")),
        'Bathrooms': int(input("Bathrooms: ")),
        'Year Built': int(input("Year Built: ")),
        'Nearby Amenities': input("Nearby Amenities: ").strip().lower(),
        'Market Trends': input("Market Trends: ").strip().lower()
    }
    
    # Convert input dictionary to DataFrame
    input_df = pd.DataFrame([user_data])
    
    # Generate and display prediction
    prediction = model_pipeline.predict(input_df)
    print(f"\n✅ Predicted Sale Price: ₹{prediction[0]:,.2f}")

# Run the prediction interface
get_user_prediction()