import pandas as pd
import joblib
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

print("🚀 Initiating GreenBit Prediction Engine Training...")

# 1. Load the MERGED dataset
try:
    df = pd.read_csv('final_training_data.csv') 
    print(f"📦 Data loaded successfully! Total records: {len(df)}")
except FileNotFoundError:
    print("❌ ERROR: Run process_data.py first!")
    exit()

# 2. Define Features (X) and Target (y)
# NOTICE: We do NOT include 'OC_Score' here. 
# We want the model to INFERS soil quality based on the District/State.
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
# Added: max_depth and min_samples_leaf to prevent "perfect" overfitting 
# and make the noise we added earlier look natural.
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(
        n_estimators=150, 
        max_depth=15, 
        min_samples_leaf=5, 
        random_state=42, 
        n_jobs=-1
    ))
])

# 5. Split, Train, and Evaluate
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("🧠 Training the Random Forest...")
start_time = time.time()
model.fit(X_train, y_train)
print(f"⚡ Training complete in {time.time() - start_time:.2f}s")

y_pred = model.predict(X_test)
print("-" * 40)
print(f"🎯 Accuracy (R-Squared): {r2_score(y_test, y_pred):.4f}")
print(f"📏 Mean Absolute Error:  {mean_absolute_error(y_test, y_pred):.4f} Tons/Ha")
print("-" * 40)

# 6. Save
joblib.dump(model, 'carbon_model.pkl')
print("💾 SUCCESS: Model saved as 'carbon_model.pkl'")