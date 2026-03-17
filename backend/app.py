import joblib
import pandas as pd
import sqlite3
import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# --- CONFIG & SECURITY ---
SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI(title="GreenBit Pro Backend")

# Add CORS Middleware so your frontend can actually talk to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL DATA LOAD (Crucial for speed!) ---
print("⏳ Loading ML Engine and Metadata...")
model = joblib.load('carbon_model.pkl')

# 🚨 THE FIX: Point to the fully merged dataset that contains all the columns!
master_df = pd.read_csv('final_training_data.csv') 

# Cache metadata arrays to memory so API routes are instant
STATES = sorted(master_df['State'].dropna().unique().tolist())
DISTRICTS = sorted(master_df['District'].dropna().unique().tolist())
CROPS = sorted(master_df['Crop'].dropna().unique().tolist())
SEASONS = sorted(master_df['Season'].dropna().unique().tolist())
print("✅ Engine and Metadata Loaded successfully!")

# --- DATABASE INIT ---
def get_db():
    conn = sqlite3.connect("carbon_vault.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

db = get_db()
db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        hashed_password TEXT
    )
""")
# Upgraded schema to match the new ML Features
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
    username: str
    password: str

class PlotCreate(BaseModel):
    plot_name: str
    state: str
    district: str
    crop: str
    season: str
    plot_yield: float # Cannot use 'yield' as it is a protected keyword in Python
    size_ha: float
    annual_rainfall: float

class CarbonReport(BaseModel):
    plot_name: str
    carbon_per_ha: float
    total_carbon: float
    estimated_revenue_inr: float

# --- AUTH UTILS ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise HTTPException(status_code=401)
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- ROUTES: AUTHENTICATION ---
@app.post("/register")
async def register(user: UserCreate):
    hashed = pwd_context.hash(user.password)
    try:
        db.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (user.username, hashed))
        db.commit()
        return {"msg": "User created successfully"}
    except:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.execute("SELECT * FROM users WHERE username = ?", (form_data.username,)).fetchone()
    if not user or not pwd_context.verify(form_data.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = jwt.encode({"sub": user['username']}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """
    Since JWTs are stateless, actual logout happens on the frontend by deleting the token.
    This route is provided for API completeness and future token blacklisting.
    """
    return {"msg": f"Goodbye {current_user}! Successfully logged out. Please remove the token from client storage."}

# --- ROUTES: METADATA DISCOVERY ---
@app.get("/metadata")
async def get_all_metadata():
    """Returns all drop-down options instantly from memory cache."""
    return {
        "states": STATES,
        "districts": DISTRICTS,
        "crops": CROPS,
        "seasons": SEASONS,
        "rainfall_range": {
            "min": float(master_df['Annual_Rainfall'].min()),
            "max": float(master_df['Annual_Rainfall'].max())
        }
    }

# --- ROUTES: PLOT MANAGEMENT ---
@app.post("/plots", response_model=dict)
async def add_plot(plot: PlotCreate, current_user: str = Depends(get_current_user)):
    user = db.execute("SELECT id FROM users WHERE username = ?", (current_user,)).fetchone()
    db.execute("""
        INSERT INTO plots (user_id, plot_name, state, district, crop, season, plot_yield, size_ha, annual_rainfall)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user['id'], plot.plot_name, plot.state.upper(), plot.district.upper(), plot.crop.upper(), plot.season.upper(), plot.plot_yield, plot.size_ha, plot.annual_rainfall))
    db.commit()
    return {"msg": f"Plot '{plot.plot_name}' added successfully"}

@app.get("/plots", response_model=List[dict])
async def list_plots(current_user: str = Depends(get_current_user)):
    user = db.execute("SELECT id FROM users WHERE username = ?", (current_user,)).fetchone()
    plots = db.execute("SELECT * FROM plots WHERE user_id = ?", (user['id'],)).fetchall()
    return [dict(p) for p in plots]

# --- ROUTES: THE AI ENGINE ---
@app.get("/calculate/{plot_id}", response_model=CarbonReport)
async def get_plot_calculation(plot_id: int, current_user: str = Depends(get_current_user)):
    user = db.execute("SELECT id FROM users WHERE username = ?", (current_user,)).fetchone()
    plot = db.execute("SELECT * FROM plots WHERE id = ? AND user_id = ?", (plot_id, user['id'])).fetchone()
    
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    # 🚨 Crucial: Maps perfectly to your 6 Random Forest features
    input_df = pd.DataFrame([{
        'State': plot['state'],
        'District': plot['district'],
        'Crop': plot['crop'],
        'Season': plot['season'],
        'Yield': plot['plot_yield'],
        'Annual_Rainfall': plot['annual_rainfall']
    }])
    
    # Predict using the saved Random Forest model
    carbon_density = model.predict(input_df)[0]
    total_c = carbon_density * plot['size_ha']
    
    return {
        "plot_name": plot['plot_name'],
        "carbon_per_ha": round(carbon_density, 4),
        "total_carbon": round(total_c, 2),
        "estimated_revenue_inr": round(total_c * 1200, 2) # Assuming ₹1200 per carbon credit
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)