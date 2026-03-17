import pandas as pd
import numpy as np
import os

DATA_DIR = "datasets"
SINGLE_CROP_FILE = os.path.join(DATA_DIR, 'apy_master_dataset.csv')
KAGGLE_RAIN_FILE = os.path.join(DATA_DIR, 'daily_rainfall.csv')

def clean_names(series):
    """Standardizes names for perfect joining."""
    cleaned = series.astype(str).str.upper().str.replace(r'[^A-Z]', '', regex=True).str.strip()
    alias_dict = {
        "ANDAMANANDNICOBARISLANDS": "ANDAMANNICOBAR",
        "JAMMUANDKASHMIR": "JAMMUKASHMIR",
        "THEDADRAANDNAGARHAVELIANDDAMANANDDIU": "DADRAANDNAGARHAVELI",
        "NCTOFDELHI": "DELHI",
        "ORISSA": "ODISHA" # Adding this just in case Kaggle uses old names
    }
    return cleaned.replace(alias_dict)

def process_crop_wide(filepath, target_year):
    df = pd.read_csv(filepath)
    year_suffix = f"{target_year}-{str(target_year + 1)[-2:]}"
    yield_col = f"Yield-{year_suffix}"
    
    if yield_col not in df.columns: return pd.DataFrame()

    cols_to_keep = ['State', 'District', 'Crop', 'Season', yield_col]
    df_year = df[cols_to_keep].copy()
    df_year.rename(columns={yield_col: 'Yield'}, inplace=True)
    
    df_year['State'] = clean_names(df_year['State'])
    df_year['District'] = clean_names(df_year['District'])
    df_year['Crop'] = df_year['Crop'].astype(str).str.upper().str.strip()
    df_year['Season'] = df_year['Season'].astype(str).str.upper().str.strip()
    
    aggregates = ['TOTAL FOOD GRAINS', 'TOTAL PULSES', 'TOTAL OIL SEEDS', 'CEREALS', 'SHREE ANNA /NUTRI CEREALS', 'NUTRI/COARSE CEREALS']
    df_year = df_year[~df_year['Crop'].isin(aggregates)]
    df_year = df_year[df_year['Season'] != 'WHOLE YEAR']
    
    df_year['Yield'] = pd.to_numeric(df_year['Yield'], errors='coerce').fillna(0)
    df_year['Year'] = target_year
    return df_year

def process_kaggle_rainfall(filepath, target_year):
    """Parses the Kaggle dataset: Extracts year from date and sums the 'actual' column."""
    df = pd.read_csv(filepath)
    
    # Convert date and extract the year
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['Year'] = df['date'].dt.year
    
    # Filter for our specific year loop
    df = df[df['Year'] == target_year].copy()
    if df.empty: return pd.DataFrame()

    # Clean state names
    df['State'] = clean_names(df['state_name'])
    df['actual'] = pd.to_numeric(df['actual'], errors='coerce').fillna(0)
    
    # Group by State and sum the daily rainfall into an annual total
    annual = df.groupby(['State', 'Year'])['actual'].sum().reset_index()
    annual.rename(columns={'actual': 'Annual_Rainfall'}, inplace=True)
    
    return annual

def process_soil(filepath):
    df = pd.read_csv(filepath)
    df['State'] = clean_names(df['State'])
    df['Total_OC_Samples'] = df['OC_High'] + df['OC_Medium'] + df['OC_Low']
    df = df[df['Total_OC_Samples'] > 0] 
    df['OC_Score'] = ((df['OC_Low'] * 0.2) + (df['OC_Medium'] * 0.5) + (df['OC_High'] * 0.8)) / df['Total_OC_Samples']
    return df[['State', 'OC_Score']].drop_duplicates()

# --- MAIN EXECUTION ---
years = [2023, 2024]
master_frames = []

print("⚙️ Processing Kaggle Rainfall and APY Crop Data...")

for year in years:
    print(f"🔄 Processing Year: {year}...")
    
    # Adjust soil path if you only have one master soil file
    soil_path = os.path.join(DATA_DIR, f'soil_nutrient_database_{year}.csv')

    df_c = process_crop_wide(SINGLE_CROP_FILE, year)
    df_r = process_kaggle_rainfall(KAGGLE_RAIN_FILE, year)
    
    if df_c.empty: continue
    if os.path.exists(soil_path):
        df_s = process_soil(soil_path)
    else:
        continue # Skip if soil doesn't exist for this year

    # --- THE BROADCAST JOIN ---
    # 1. Join Crops with Soil (Both have State)
    m1 = pd.merge(df_c, df_s, on='State', how='inner')
    
    # 2. Join with Rain (State-Level). 
    # Because Rain lacks District, merging on State broadcasts the state rain to all districts!
    m2 = pd.merge(m1, df_r, on=['State', 'Year'], how='left')
    
    master_frames.append(m2)

# --- FINAL CONSOLIDATION & CALCULATION ---
if master_frames:
    final_df = pd.concat(master_frames, ignore_index=True)
    
    # Global fallback just in case Kaggle missed a state
    final_df['Annual_Rainfall'] = final_df['Annual_Rainfall'].fillna(1050.0)

    # 🧠 Target Calculation
    base_carbon = final_df['OC_Score'] * 39.5
    yield_modifier = np.log1p(final_df['Yield']) * 0.02 
    rain_modifier = (final_df['Annual_Rainfall'] / 1000) * 0.05
    final_df['Carbon_Tons_Ha'] = base_carbon * (1 + yield_modifier + rain_modifier)

    # Export
    output_cols = ['State', 'District', 'Crop', 'Season', 'Yield', 'Year', 'Annual_Rainfall', 'OC_Score', 'Carbon_Tons_Ha']
    
    final_output = final_df[output_cols].dropna().drop_duplicates()
    final_output.to_csv('final_training_data.csv', index=False)
    
    print(f"🎉 SUCCESS: 'final_training_data.csv' created with {len(final_output)} records.")
else:
    print("❌ ERROR: Data merge failed.")