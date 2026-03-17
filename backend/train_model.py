import pandas as pd
import joblib
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

print("🚀 Initiating CarbonTrace Prediction Engine Training...")

# 1. Load the MERGED dataset (NOT the raw Kaggle file)
try:
    # THIS IS THE LINE THAT CHANGED
    df = pd.read_csv('final_training_data.csv') 
    print(f"📦 Data loaded successfully! Total agronomic records: {len(df)}")
except FileNotFoundError:
    print("❌ ERROR: 'final_training_data.csv' not found. You need to run process_data.py first!")
    exit()

# Drop any accidental blank rows
df = df.dropna(subset=['Carbon_Tons_Ha'])

# 2. Define Features (X) and Target (y)
X = df[['State', 'District', 'Crop', 'Season', 'Yield', 'Annual_Rainfall']]
y = df['Carbon_Tons_Ha']

# 3. Build the Preprocessing Pipeline
categorical_features = ['State', 'District', 'Crop', 'Season']
numerical_features = ['Yield', 'Annual_Rainfall']

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ('num', StandardScaler(), numerical_features)
    ])

# 4. Construct the Random Forest Pipeline
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])

# 5. Split Data (80% Training, 20% Testing)
print("✂️ Splitting data into Training (80%) and Testing (20%) sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Train the Model
print("🧠 Training the Random Forest (Using all CPU cores)...")
start_time = time.time()
model.fit(X_train, y_train)
training_time = time.time() - start_time
print(f"⚡ Training complete in {training_time:.2f} seconds!")

# 7. Evaluate the Model
print("📊 Evaluating Model Accuracy...")
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print("-" * 40)
print(f"🎯 Accuracy (R-Squared): {r2:.4f}")
print(f"📏 Mean Absolute Error:  {mae:.4f} Tons/Ha")
print("-" * 40)

# 8. Save the Engine
model_filename = 'carbon_model.pkl'
joblib.dump(model, model_filename)
print(f"💾 SUCCESS: Model saved as '{model_filename}'! Ready for the FastAPI Backend.")