import joblib
import pandas as pd
import sqlite3
import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# --- CONFIG & SECURITY ---
SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI(title="GreenBit Pro Backend")

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
# UPDATED: Table now uses 'email' instead of 'username'
db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        hashed_password TEXT
    )
""")
db.execute("""
    CREATE TABLE IF NOT EXISTS plots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plot_name TEXT,
        state TEXT,
        district TEXT,
        crop TEXT,
        season TEXT,
        plot_yield REAL,
        size_ha REAL,
        annual_rainfall REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")
db.commit()

# --- SCHEMAS ---
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str
class PlotCreate(BaseModel):
    plot_name: str
    state: str
    district: str
    crop: str
    season: str
    size_ha: float
    # 🚨 THE FIX: Make these optional so the frontend doesn't have to send them
    plot_yield: Optional[float] = None 
    annual_rainfall: Optional[float] = None
class CarbonReport(BaseModel):
    plot_name: str; carbon_per_ha: float; total_carbon: float; estimated_revenue_inr: float

# --- AUTH UTILS ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401)
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- ROUTES: AUTHENTICATION ---
@app.post("/register")
async def register(user: UserCreate):
    # Truncate for bcrypt compatibility
    safe_password = user.password.encode('utf-8')[:72].decode('utf-8', 'ignore')
    hashed = pwd_context.hash(safe_password)
    try:
        db.execute("INSERT INTO users (email, hashed_password) VALUES (?, ?)", (user.email.lower(), hashed))
        db.commit()
        return {"msg": "User created successfully"}
    except:
        raise HTTPException(status_code=400, detail="Email already registered")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm.username will contain the email string
    user = db.execute("SELECT * FROM users WHERE email = ?", (form_data.username.lower(),)).fetchone()
    
    safe_password = form_data.password.encode('utf-8')[:72].decode('utf-8', 'ignore')
    
    if not user or not pwd_context.verify(safe_password, user['hashed_password']):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Standard JWT 'sub' claim uses the unique identifier (email)
    access_token = jwt.encode({"sub": user['email']}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

# --- ROUTES: METADATA & PLOTS ---
@app.get("/metadata")
async def get_all_metadata():
    return {"states": STATES, "districts": DISTRICTS, "crops": CROPS, "seasons": SEASONS}

@app.post("/plots")
async def add_plot(plot: PlotCreate, current_email: str = Depends(get_current_user)):
    user = db.execute("SELECT id FROM users WHERE email = ?", (current_email,)).fetchone()
    
    # 🔍 INTERNAL LOOKUP: Find the regional constants
    match = master_df[
        (master_df['State'] == plot.state.upper()) & 
        (master_df['District'] == plot.district.upper()) & 
        (master_df['Crop'] == plot.crop.upper()) & 
        (master_df['Season'] == plot.season.upper())
    ]
    
    # Use median values from the dataset; default to safety if no match
    auto_yield = float(match['Yield'].median()) if not match.empty else 1.2
    auto_rain = float(match['Annual_Rainfall'].median()) if not match.empty else 1050.0

    # 💾 SAVE: The user only sent 4 things, we save all 8
    db.execute("""
        INSERT INTO plots (user_id, plot_name, state, district, crop, season, plot_yield, size_ha, annual_rainfall)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user['id'], plot.plot_name, plot.state.upper(), plot.district.upper(), 
          plot.crop.upper(), plot.season.upper(), auto_yield, plot.size_ha, auto_rain))
    db.commit()
    
    return {"msg": "Plot analyzed and saved successfully using regional environmental data."}

@app.get("/plots")
async def list_plots(current_email: str = Depends(get_current_user)):
    user = db.execute("SELECT id FROM users WHERE email = ?", (current_email,)).fetchone()
    plots = db.execute("SELECT * FROM plots WHERE user_id = ?", (user['id'],)).fetchall()
    return [dict(p) for p in plots]

@app.get("/calculate/{plot_id}", response_model=CarbonReport)
async def get_plot_calculation(plot_id: int, current_email: str = Depends(get_current_user)):
    user = db.execute("SELECT id FROM users WHERE email = ?", (current_email,)).fetchone()
    plot = db.execute("SELECT * FROM plots WHERE id = ? AND user_id = ?", (plot_id, user['id'])).fetchone()
    
    if not plot: raise HTTPException(status_code=404, detail="Plot not found")

    input_df = pd.DataFrame([{
        'State': plot['state'], 'District': plot['district'], 'Crop': plot['crop'],
        'Season': plot['season'], 'Yield': plot['plot_yield'], 'Annual_Rainfall': plot['annual_rainfall']
    }])
    
    carbon_density = model.predict(input_df)[0]
    total_c = carbon_density * plot['size_ha']
    
    return {
        "plot_name": plot['plot_name'],
        "carbon_per_ha": round(carbon_density, 4),
        "total_carbon": round(total_c, 2),
        "estimated_revenue_inr": round(total_c * 1200, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)