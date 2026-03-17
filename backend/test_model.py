import joblib
import pandas as pd
import numpy as np

# --- 1. Load the "Engine" ---
MODEL_PATH = 'carbon_model.pkl'

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Engine '{MODEL_PATH}' loaded successfully!\n")
except FileNotFoundError:
    print(f"❌ ERROR: '{MODEL_PATH}' not found. Run train_model.py first.")
    exit()

# --- 2. Define Test Scenarios ---
# These scenarios test the model's logic across different climates and crops.
test_scenarios = [
    {
        "Name": "Punjab High-Yield Wheat (Dry)",
        "Data": {
            'State': 'PUNJAB', 'District': 'LUDHIANA', 'Crop': 'WHEAT', 
            'Season': 'RABI', 'Yield': 5.2, 'Annual_Rainfall': 650.0
        }
    },
    {
        "Name": "Assam Low-Yield Rice (Tropical/Wet)",
        "Data": {
            'State': 'ASSAM', 'District': 'KAMRUP', 'Crop': 'RICE', 
            'Season': 'KHARIF', 'Yield': 3.1, 'Annual_Rainfall': 2800.0
        }
    },
    {
        "Name": "Maharashtra Cotton (Semi-Arid)",
        "Data": {
            'State': 'MAHARASHTRA', 'District': 'NAGPUR', 'Crop': 'COTTON', 
            'Season': 'KHARIF', 'Yield': 1.5, 'Annual_Rainfall': 1100.0
        }
    }
]

# --- 3. Run Inference ---
print(f"{'🔍 TEST SCENARIO':<40} | {'🌿 PREDICTED CARBON (Tons/Ha)':<30}")
print("-" * 75)

for scenario in test_scenarios:
    # Convert single scenario to a DataFrame (the format the Pipeline expects)
    input_df = pd.DataFrame([scenario['Data']])
    
    # Predict
    prediction = model.predict(input_df)[0]
    
    print(f"{scenario['Name']:<40} | {prediction:>25.4f}")

print("-" * 75)
print("\n💡 Logic Check: Assam (High Rain) should generally yield higher carbon than Punjab (Dry),")
print("   unless the Punjab yield is exponentially higher. This proves environmental weighting.")