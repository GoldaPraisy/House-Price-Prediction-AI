import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

MODEL_FILE = 'model.joblib'
DATA_FILE = 'tamilnadu_house_data.csv'

# Global variables for model and statistics
model_pipeline = None
model_accuracy = 0.0
stats_cache = {}

def train_and_initialize():
    global model_pipeline, model_accuracy, stats_cache
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return False
    
    # Load dataset
    df = pd.read_csv(DATA_FILE)
    
    # Preprocessing column headers (strip spaces)
    df.columns = df.columns.str.strip()
    
    categorical_cols = ['City', 'Neighborhood', 'Pincode', 'Nearby Amenities', 'Market Trends']
    numerical_cols = ['Property Size (sqft)', 'Lot Size', 'Bedrooms', 'Bathrooms', 'Year Built']
    
    # Clean text columns
    for col in categorical_cols:
        df[col] = df[col].astype(str).str.strip().str.lower()
        
    X = df[categorical_cols + numerical_cols]
    y = df['Sale Price']
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
        ])
    
    # Pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Split to compute accuracy
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    model_accuracy = r2_score(y_test, y_pred)
    print(f"Model trained successfully. R2 score: {model_accuracy:.4f}")
    
    # Save the pipeline trained on the entire dataset for better prediction accuracy
    pipeline.fit(X, y)
    joblib.dump(pipeline, MODEL_FILE)
    model_pipeline = pipeline
    
    # Compute stats for the dashboard
    # 1. City-wise average price
    city_stats = df.groupby('City')['Sale Price'].agg(['mean', 'count']).reset_index()
    city_stats['City'] = city_stats['City'].str.title()
    city_stats = city_stats.sort_values(by='mean', ascending=False)
    
    # 2. Market trend breakdown
    trend_counts = df['Market Trends'].value_counts(normalize=True).to_dict()
    market_trends = {k.title(): float(v * 100) for k, v in trend_counts.items()}
    
    # 3. Overall numbers
    stats_cache = {
        'total_listings': int(len(df)),
        'average_price': float(df['Sale Price'].mean()),
        'min_price': float(df['Sale Price'].min()),
        'max_price': float(df['Sale Price'].max()),
        'model_accuracy': float(model_accuracy * 100),
        'city_stats': city_stats.to_dict(orient='records'),
        'market_trends': market_trends
    }
    return True

# Initialize on start
train_and_initialize()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not stats_cache:
        success = train_and_initialize()
        if not success:
            return jsonify({"error": "Failed to initialize dataset and model"}), 500
    return jsonify(stats_cache)

@app.route('/api/predict', methods=['POST'])
def predict():
    global model_pipeline
    if model_pipeline is None:
        success = train_and_initialize()
        if not success:
            return jsonify({"error": "Model not loaded or trained"}), 500
            
    try:
        data = request.get_json()
        
        # Parse inputs
        # Expected structure:
        # {
        #   'City': 'Chennai',
        #   'Neighborhood': 'Chennai Sector 10',
        #   'Pincode': '60541',
        #   'Property Size (sqft)': 3000,
        #   'Lot Size': 4000,
        #   'Bedrooms': 4,
        #   'Bathrooms': 3,
        #   'Year Built': 2005,
        #   'Nearby Amenities': 'none',
        #   'Market Trends': 'rising'
        # }
        
        # Build user dataframe
        user_data = {
            'City': str(data.get('City', '')).strip().lower(),
            'Neighborhood': str(data.get('Neighborhood', '')).strip().lower(),
            'Pincode': str(data.get('Pincode', '')).strip().lower(),
            'Nearby Amenities': str(data.get('Nearby Amenities', '')).strip().lower(),
            'Market Trends': str(data.get('Market Trends', '')).strip().lower(),
            'Property Size (sqft)': float(data.get('Property Size (sqft)', 0)),
            'Lot Size': float(data.get('Lot Size', 0)),
            'Bedrooms': int(data.get('Bedrooms', 0)),
            'Bathrooms': int(data.get('Bathrooms', 0)),
            'Year Built': int(data.get('Year Built', 2000))
        }
        
        # Convert to dataframe with matching columns
        # Column names must match training columns
        input_df = pd.DataFrame([user_data])
        
        # Predict
        predicted_price = model_pipeline.predict(input_df)[0]
        
        # Add quick confidence interval or score based on R2 and input proximity
        return jsonify({
            "predicted_price": float(predicted_price),
            "currency": "INR",
            "status": "success"
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
