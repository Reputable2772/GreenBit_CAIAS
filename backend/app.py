import joblib
import pandas as pd
import sqlite3
import os
import numpy as np
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG & SECURITY ---
SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY")
ALGORITHM = "HS256"

# THE FIX: Using the modern pwdlib instead of passlib
pwd_context = PasswordHash((BcryptHasher(),))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="GreenBit Pro: Investment-Grade Carbon Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL DATA LOAD ---
print("⏳ Loading ML Engine and Metadata...")
try:
    model = joblib.load('carbon_model.pkl')
    master_df = pd.read_csv('final_training_data.csv') 
    
    STATES = sorted(master_df['State'].dropna().unique().tolist())
    DISTRICTS = sorted(master_df['District'].dropna().unique().tolist())
    CROPS = sorted(master_df['Crop'].dropna().unique().tolist())
    SEASONS = sorted(master_df['Season'].dropna().unique().tolist())
    print("✅ Engine and Metadata Loaded successfully!")
except Exception as e:
    print(f"❌ ERROR: Pre-loading failed: {e}")

# --- DATABASE INIT ---
def get_db():
    conn = sqlite3.connect("carbon_vault.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

db = get_db()
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, hashed_password TEXT)")
db.execute("""
    CREATE TABLE IF NOT EXISTS plots (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, plot_name TEXT, state TEXT, district TEXT, 
        crop TEXT, season TEXT, plot_yield REAL, size_ha REAL, annual_rainfall REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")
db.commit()

# --- SCHEMAS ---
class UserCreate(BaseModel):
    email: EmailStr; password: str

class PlotCreate(BaseModel):
    plot_name: str; state: str; district: str; crop: str; season: str; size_ha: float
    plot_yield: Optional[float] = None; annual_rainfall: Optional[float] = None

class CarbonReport(BaseModel):
    plot_name: str
    carbon_per_ha: float         # Match Frontend
    total_carbon: float          # Match Frontend
    lower_carbon_ha: float       # Match Frontend
    mean_carbon_ha: float        # Match Frontend
    upper_carbon_ha: float       # Match Frontend
    estimated_revenue_inr: float
    reliability_rating: str

# --- AUTH UTILS ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401)
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- ROUTES ---
@app.post("/register")
async def register(user: UserCreate):
    # CLEANER LOGIC: pwdlib handles the string hashing directly and safely
    hashed = pwd_context.hash(user.password)
    try:
        db.execute("INSERT INTO users (email, hashed_password) VALUES (?, ?)", (user.email.lower(), hashed))
        db.commit()
        return {"msg": "User created successfully"}
    except:
        raise HTTPException(status_code=400, detail="Email already registered")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.execute("SELECT * FROM users WHERE email = ?", (form_data.username.lower(),)).fetchone()
    
    # CLEANER LOGIC: Simple, secure verification without byte-slicing hacks
    if not user or not pwd_context.verify(form_data.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    access_token = jwt.encode({"sub": user['email']}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/metadata")
async def get_all_metadata():
    return {"states": STATES, "districts": DISTRICTS, "crops": CROPS, "seasons": SEASONS}

@app.post("/plots")
async def add_plot(plot: PlotCreate, current_email: str = Depends(get_current_user)):
    user_record = db.execute("SELECT id FROM users WHERE email = ?", (current_email,)).fetchone()
    match = master_df[(master_df['State'] == plot.state.upper()) & (master_df['District'] == plot.district.upper()) & 
                      (master_df['Crop'] == plot.crop.upper()) & (master_df['Season'] == plot.season.upper())]
    auto_yield = float(match['Yield'].median()) if not match.empty else 1.2
    auto_rain = float(match['Annual_Rainfall'].median()) if not match.empty else 1050.0
    db.execute("""
        INSERT INTO plots (user_id, plot_name, state, district, crop, season, plot_yield, size_ha, annual_rainfall)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_record['id'], plot.plot_name, plot.state.upper(), plot.district.upper(), 
          plot.crop.upper(), plot.season.upper(), auto_yield, plot.size_ha, auto_rain))
    db.commit()
    return {"msg": "Plot analyzed and saved successfully."}

@app.get("/plots")
async def list_plots(current_email: str = Depends(get_current_user)):
    user_record = db.execute("SELECT id FROM users WHERE email = ?", (current_email,)).fetchone()
    plots = db.execute("SELECT * FROM plots WHERE user_id = ?", (user_record['id'],)).fetchall()
    return [dict(p) for p in plots]

# --- THE ANALYTICS ENGINE (INVESTMENT GRADE) ---
@app.get("/calculate/{plot_id}", response_model=CarbonReport)
async def get_plot_calculation(plot_id: int, current_email: str = Depends(get_current_user)):
    user_record = db.execute("SELECT id FROM users WHERE email = ?", (current_email,)).fetchone()
    plot = db.execute("SELECT * FROM plots WHERE id = ? AND user_id = ?", (plot_id, user_record['id'])).fetchone()
    
    if not plot: raise HTTPException(status_code=404, detail="Plot not found")

    input_df = pd.DataFrame([{
        'State': plot['state'], 'District': plot['district'], 'Crop': plot['crop'],
        'Season': plot['season'], 'Yield': plot['plot_yield'], 'Annual_Rainfall': plot['annual_rainfall']
    }])
    
    try:
        # Step 1: Pre-process features
        X_transformed = model.named_steps['preprocessor'].transform(input_df)
        rf_regressor = model.named_steps['regressor']
        
        # Step 2: Ensemble Prediction Logic
        tree_preds = [tree.predict(X_transformed)[0] for tree in rf_regressor.estimators_]
        
        # Step 3: Carbon Market Logic
        mean_val = np.mean(tree_preds)
    
        mean_val = np.mean(tree_preds)
        p10 = np.percentile(tree_preds, 10)
        p90 = np.percentile(tree_preds, 90)

        # Investment Logic
        buffer_deduction = p10 * 0.20
        net_ha = p10 - buffer_deduction
        total_net_credits = net_ha * plot['size_ha']

        return {
            "plot_name": plot['plot_name'],
            "carbon_per_ha": round(mean_val, 4),      # This fills your "Carbon/ha" card
            "total_carbon": round(total_net_credits, 2), # This fills your "Total" card
            "lower_carbon_ha": round(p10, 4),
            "mean_carbon_ha": round(mean_val, 4),
            "upper_carbon_ha": round(p90, 4),
            "estimated_revenue_inr": round(total_net_credits * 1200, 2),
            "reliability_rating": "A (High)" # Or your CV logic
        }  
    except Exception as e:
        print(f"🔥 Error during calculation: {e}")
        raise HTTPException(status_code=500, detail="Model processing failed.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
