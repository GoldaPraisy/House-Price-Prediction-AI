# Import libraries
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
data = pd.read_csv("tamilnadu_house_data.csv")

# Display dataset information
print("Dataset Info:")
print(data.info())

print("\nFirst 5 rows:")
print(data.head())

print("\nStatistical Summary:")
print(data.describe())

# -------------------------------
# 1. Scatter Plot
# Property Size vs Sale Price
# -------------------------------

plt.figure(figsize=(8,5))
plt.scatter(data["Property Size (sqft)"], data["Sale Price"])
plt.title("Property Size vs House Price")
plt.xlabel("Property Size (sqft)")
plt.ylabel("Sale Price")
plt.show()

# -------------------------------
# 2. Bar Chart
# Average Price by City
# -------------------------------

avg_price_city = data.groupby("City")["Sale Price"].mean()

plt.figure(figsize=(10,5))
avg_price_city.plot(kind="bar")
plt.title("Average House Price by City")
plt.xlabel("City")
plt.ylabel("Average Sale Price")
plt.show()

# -------------------------------
# 3. Pie Chart
# Market Trend Distribution
# -------------------------------

trend_count = data["Market Trends"].value_counts()

plt.figure(figsize=(6,6))
plt.pie(trend_count, labels=trend_count.index, autopct='%1.1f%%')
plt.title("Market Trend Distribution")
plt.show()

# -------------------------------
# 4. Correlation Heatmap
# -------------------------------

numeric_data = data.select_dtypes(include=['int64','float64'])

plt.figure(figsize=(8,6))
sns.heatmap(numeric_data.corr(), annot=True, cmap="coolwarm")
plt.title("Feature Correlation Heatmap")
plt.show()