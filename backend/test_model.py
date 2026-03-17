import pandas as pd
import joblib

print("🧪 Loading CarbonTrace ML Engine for Sanity Testing...\n")

# Load the saved model
try:
    model = joblib.load('carbon_model.pkl')
except FileNotFoundError:
    print("❌ ERROR: 'carbon_model.pkl' not found.")
    exit()

# Define 3 distinct test scenarios to prove the model adapts to different climates
scenarios = [
    {
        "Scenario": "🌾 Punjab Wheat (High Yield, Low Rain)",
        "State": "PUNJAB",
        "District": "LUDHIANA",
        "Crop": "WHEAT",
        "Season": "RABI",
        "Yield": 5.2,          # High yield
        "Annual_Rainfall": 650 # Lower rainfall
    },
    {
        "Scenario": "🌧️ Assam Rice (Moderate Yield, Massive Rain)",
        "State": "ASSAM",
        "District": "DIBRUGARH",
        "Crop": "RICE",
        "Season": "KHARIF",
        "Yield": 3.1,           # Moderate yield
        "Annual_Rainfall": 2800 # Very high rainfall
    },
    {
        "Scenario": "🧵 Maharashtra Cotton (Low Yield, Moderate Rain)",
        "State": "MAHARASHTRA",
        "District": "NAGPUR",
        "Crop": "COTTON",
        "Season": "KHARIF",
        "Yield": 1.5,           # Lower yield
        "Annual_Rainfall": 1100 # Moderate rainfall
    }
]

# Convert scenarios to a Pandas DataFrame
test_df = pd.DataFrame(scenarios)

# We only pass the features the model was trained on
features = test_df[['State', 'District', 'Crop', 'Season', 'Yield', 'Annual_Rainfall']]

# Run the predictions
predictions = model.predict(features)

# Print the results beautifully
print("📊 --- TEST RESULTS --- 📊\n")
for i, row in test_df.iterrows():
    print(f"📍 {row['Scenario']}")
    print(f"   Inputs: {row['Yield']} Tons/Ha Yield | {row['Annual_Rainfall']}mm Rain")
    print(f"   🌿 PREDICTED CARBON: {predictions[i]:.4f} Tons/Hectare")
    print(f"   💰 EST. REVENUE: ₹{predictions[i] * 1200:,.2f} per Hectare")
    print("-" * 50)

print("\n✅ Testing Complete. If the carbon numbers vary logically based on the inputs, your AI is bulletproof.")