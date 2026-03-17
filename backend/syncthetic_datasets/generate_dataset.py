import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)
n_samples = 1000

# 1. Define Categories
crop_types = ['Wheat', 'Corn', 'Soybeans', 'Rice', 'Alfalfa (Cover Crop)']
soil_types = ['Sandy', 'Loamy', 'Clay', 'Peaty', 'Saline']

# 2. Generate random inputs
crops = np.random.choice(crop_types, n_samples)
soils = np.random.choice(soil_types, n_samples)
rainfall = np.random.normal(loc=800, scale=200, size=n_samples).clip(200, 2000) # Rainfall in mm
ndvi = np.random.uniform(low=0.2, high=0.9, size=n_samples) # NDVI score

# 3. Define the hidden logic (Multipliers for carbon retention)
crop_mult = {'Wheat': 1.2, 'Corn': 1.5, 'Soybeans': 1.8, 'Rice': 1.1, 'Alfalfa (Cover Crop)': 2.5}
soil_mult = {'Sandy': 0.7, 'Loamy': 1.5, 'Clay': 1.2, 'Peaty': 2.0, 'Saline': 0.5}

# 4. Calculate target variable (Carbon Captured in tons per hectare)
carbon_captured = []
for i in range(n_samples):
    # Base calculation based on crop and soil pairing
    base = crop_mult[crops[i]] * soil_mult[soils[i]]
    # Bonus for healthy vegetation (NDVI) and rainfall
    ndvi_bonus = ndvi[i] * 3
    rain_bonus = rainfall[i] / 500
    # Add realistic noise
    noise = np.random.normal(0, 0.5)
    
    total_carbon = base + ndvi_bonus + rain_bonus + noise
    # Ensure no negative carbon values and round to 2 decimals
    carbon_captured.append(max(0.1, round(total_carbon, 2))) 

# 5. Create DataFrame and export
df = pd.DataFrame({
    'Crop_Type': crops,
    'Soil_Type': soils,
    'Rainfall_mm': np.round(rainfall, 1),
    'NDVI_Score': np.round(ndvi, 3),
    'Carbon_Captured_Tons_Per_Ha': carbon_captured
})

# Save to CSV
df.to_csv('synthetic_carbon_data.csv', index=False)
print("Dataset created successfully! Here are the first 5 rows:")
print(df.head())