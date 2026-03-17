import pandas as pd
import os

DATA_DIR = "datasets"
CROP_FILE = os.path.join(DATA_DIR, "apy_master_dataset.csv")
RAIN_FILE = os.path.join(DATA_DIR, "daily_rainfall.csv")

# 🚨 All 36 Indian States & UTs
MASTER_STATES = [
    "ANDAMANNICOBAR", "ANDHRAPRADESH", "ARUNACHALPRADESH", "ASSAM", "BIHAR",
    "CHANDIGARH", "CHHATTISGARH", "DADRAANDNAGARHAVELI", "DELHI", "GOA",
    "GUJARAT", "HARYANA", "HIMACHALPRADESH", "JAMMUKASHMIR", "JHARKHAND",
    "KARNATAKA", "KERALA", "LADAKH", "LAKSHADWEEP", "MADHYAPRADESH",
    "MAHARASHTRA", "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND",
    "ODISHA", "PUDUCHERRY", "PUNJAB", "RAJASTHAN", "SIKKIM",
    "TAMILNADU", "TELANGANA", "TRIPURA", "UTTARPRADESH", "UTTARAKHAND",
    "WESTBENGAL"
]

def clean_for_match(series):
    cleaned = series.astype(str).str.upper().str.replace(r'[^A-Z]', '', regex=True).str.strip()
    alias_dict = {
        "ANDAMANANDNICOBARISLANDS": "ANDAMANNICOBAR",
        "JAMMUANDKASHMIR": "JAMMUKASHMIR",
        "THEDADRAANDNAGARHAVELIANDDAMANANDDIU": "DADRAANDNAGARHAVELI",
        "NCTOFDELHI": "DELHI",
        "ORISSA": "ODISHA" 
    }
    return cleaned.replace(alias_dict)

print("🔍 Triaging National Data Coverage...\n")

# 1. Load Crop
if not os.path.exists(CROP_FILE):
    states_crop = set()
else:
    df_crop = pd.read_csv(CROP_FILE)
    crop_state_col = 'State_Name' if 'State_Name' in df_crop.columns else 'State'
    states_crop = set(clean_for_match(df_crop[crop_state_col]).dropna().unique())

# 2. Load Rain (Kaggle)
if not os.path.exists(RAIN_FILE):
    df_rain_master = None
else:
    df_rain_master = pd.read_csv(RAIN_FILE)
    df_rain_master['date'] = pd.to_datetime(df_rain_master['date'], errors='coerce')
    df_rain_master['Year'] = df_rain_master['date'].dt.year
    df_rain_master['State_Standard'] = clean_for_match(df_rain_master['state_name'])

years = [2023, 2024]

for year in years:
    print(f"{'='*60}")
    print(f"🗓️  COVERAGE REPORT FOR YEAR: {year}")
    print(f"{'='*60}")
    
    soil_file = os.path.join(DATA_DIR, f"soil_nutrient_database_{year}.csv")
    
    # 3. Extract Rain & Soil States
    if df_rain_master is not None:
        states_rain = set(df_rain_master[df_rain_master['Year'] == year]['State_Standard'].dropna().unique())
    else:
        states_rain = set()

    if os.path.exists(soil_file):
        df_soil = pd.read_csv(soil_file)
        states_soil = set(clean_for_match(df_soil['State']).dropna().unique())
    else:
        states_soil = set()

    # 4. Triage the States
    perfect_states = []
    missing_states = []
    partial_states = []
    
    for state in sorted(MASTER_STATES):
        in_crop = state in states_crop
        in_rain = state in states_rain
        in_soil = state in states_soil
        
        if in_crop and in_rain and in_soil:
            perfect_states.append(state)
        elif not in_crop and not in_rain and not in_soil:
            missing_states.append(state)
        else:
            partial_states.append({
                "State": state,
                "Crop": "✅" if in_crop else "❌",
                "Rain": "✅" if in_rain else "❌",
                "Soil": "✅" if in_soil else "❌",
            })

    # 5. Print Output
    print(f"✅ PERFECT MATCHES ({len(perfect_states)}/36) - Ready for ML:")
    print("   " + ", ".join(perfect_states) if perfect_states else "   None")
    print("\n")
    
    print(f"❌ COMPLETELY MISSING ({len(missing_states)}/36) - No data in any file:")
    print("   " + ", ".join(missing_states) if missing_states else "   None")
    print("\n")
    
    if partial_states:
        print(f"⚠️ PARTIAL DATA ({len(partial_states)}/36) - Missing from at least one:")
        df_partial = pd.DataFrame(partial_states)
        print("-" * 45)
        print(df_partial.to_string(index=False))
        print("-" * 45 + "\n")