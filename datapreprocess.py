# Import Libraries
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load Dataset
data = pd.read_csv("tamilnadu_house_data.csv")

print("Original Dataset")
print(data.head())

# -------------------------------
# 1. Data Cleaning
# -------------------------------

# Remove duplicate rows
data = data.drop_duplicates()

# Remove unnecessary spaces in column names
data.columns = data.columns.str.strip()

print("After Cleaning:")
print(data.head())

# -------------------------------
# 2. Handling Missing Values
# -------------------------------

# Check missing values
print("Missing Values:")
print(data.isnull().sum())

# Fill numerical missing values with median
data["Property Size (sqft)"].fillna(data["Property Size (sqft)"].median(), inplace=True)
data["Lot Size"].fillna(data["Lot Size"].median(), inplace=True)
data["Bedrooms"].fillna(data["Bedrooms"].median(), inplace=True)
data["Bathrooms"].fillna(data["Bathrooms"].median(), inplace=True)

# Fill categorical missing values with mode
data["City"].fillna(data["City"].mode()[0], inplace=True)
data["Neighborhood"].fillna(data["Neighborhood"].mode()[0], inplace=True)
data["Market Trends"].fillna(data["Market Trends"].mode()[0], inplace=True)

# -------------------------------
# 3. Encoding Categorical Features
# -------------------------------

label_encoder = LabelEncoder()

data["City"] = label_encoder.fit_transform(data["City"])
data["Neighborhood"] = label_encoder.fit_transform(data["Neighborhood"])
data["Market Trends"] = label_encoder.fit_transform(data["Market Trends"])
data["Nearby Amenities"] = label_encoder.fit_transform(data["Nearby Amenities"])

# -------------------------------
# 4. Feature Selection
# -------------------------------

X = data.drop("Sale Price", axis=1)
y = data["Sale Price"]

print("Features for Model:")
print(X.head())

print("Target Variable:")
print(y.head())

# -------------------------------
# Save Preprocessed Dataset
# -------------------------------

data.to_csv("clean_house_price_dataset.csv", index=False)

print("Data Preprocessing Completed Successfully")