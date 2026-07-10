import pandas as pd
import numpy as np
import random

# List of all 38 Districts in Tamil Nadu
districts = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", 
    "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", "Karur", "Krishnagiri", 
    "Madurai", "Mayiladuthurai", "Nagapattinam", "Kanniyakumari", "Namakkal", 
    "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", 
    "Tenkasi", "Thanjavur", "Theni", "Thiruvallur", "Thiruvarur", "Thoothukudi", 
    "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", "Tiruvannamalai", 
    "The Nilgiris", "Vellore", "Viluppuram", "Virudhunagar"
]

# Mapping districts to approximate price per sqft (weighted for realism)
price_mapping = {
    "Chennai": 8500, "Coimbatore": 5500, "Madurai": 4500, "Tiruchirappalli": 4200,
    "Chengalpattu": 5000, "Kancheepuram": 4800, "The Nilgiris": 6000, "Salem": 3800,
    "Tiruppur": 4000, "Erode": 3500, "Vellore": 3600, "Thoothukudi": 3200
}
default_price = 2800 # For rural districts

# Generate 1200 rows of data
data = []
for i in range(1200):
    city = random.choice(districts)
    base_price = price_mapping.get(city, default_price)
    
    # Randomly vary the attributes
    sqft = random.randint(600, 4500)
    lot_size = sqft + random.randint(200, 1000)
    rooms = random.randint(1, 5)
    baths = max(1, rooms - random.randint(0, 1))
    year = random.randint(1990, 2024)
    
    # Calculate Sale Price with some "noise" for realism
    sale_price = (sqft * base_price) + (rooms * 100000) + random.randint(-50000, 50000)
    
    row = {
        'Sale Price': round(sale_price, -3),
        'City': city,
        'Neighborhood': f"{city} Sector {random.randint(1, 10)}",
        'Pincode': f"6{random.randint(0, 4)}{random.randint(100, 999)}", # TN Pincodes start with 6
        'Property Size (sqft)': sqft,
        'Lot Size': lot_size,
        'Bedrooms': rooms,
        'Bathrooms': baths,
        'Year Built': year,
        'Nearby Amenities': random.choice(['Parks, School', 'Hospital, Mall', 'Market, Bus Stand', 'Temple, Gym', 'None']),
        'Market Trends': random.choice(['Rising', 'Stable', 'Declining'])
    }
    data.append(row)

df = pd.DataFrame(data)
df.to_csv('tamilnadu_house_data.csv', index=False)
print("Dataset 'tamilnadu_house_data.csv' created successfully with 1200 rows!")