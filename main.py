from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
import pandas as pd

# Database URL
DATABASE_URL = "postgresql://car_user:FFiCalDwRyZwiJKt5hjpsOvAaiL6sBoL@dpg-d1de9eer433s73f6bt50-a.oregon-postgres.render.com/car_api_l6s0"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Car model
class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    make = Column(String)
    model = Column(String)
    category = Column(String)

# Create table if not exists
Base.metadata.create_all(bind=engine)

# Load data from Excel into DB if empty
def load_data_once():
    db = SessionLocal()
    count = db.query(Car).first()
    if not count:
        df = pd.read_excel("cars.xlsx")
        for _, row in df.iterrows():
            car = Car(
                year=int(row['year']),
                make=str(row['make']),
                model=str(row['model']),
                category=str(row['category'])
            )
            db.add(car)
        db.commit()
    db.close()

# FastAPI app
app = FastAPI()

# CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load once
load_data_once()

@app.get("/")
def root():
    return {"message": "Car API is live"}

@app.get("/years")
def get_years():
    db = SessionLocal()
    years = db.query(Car.year).distinct().order_by(Car.year).all()
    db.close()
    return [y[0] for y in years]

@app.get("/makes")
def get_makes(year: int = Query(...)):
    db = SessionLocal()
    makes = db.query(Car.make).filter(Car.year == year).distinct().order_by(Car.make).all()
    db.close()
    return [m[0] for m in makes]

@app.get("/models")
def get_models(year: int = Query(...), make: str = Query(...)):
    db = SessionLocal()
    models = db.query(Car.model).filter(Car.year == year, Car.make == make).distinct().order_by(Car.model).all()
    db.close()
    return [m[0] for m in models]

@app.get("/car")
def get_car(year: int, make: str, model: str):
    db = SessionLocal()
    car = db.query(Car).filter(Car.year == year, Car.make == make, Car.model == model).first()
    db.close()
    if car:
        return {
            "year": car.year,
            "make": car.make,
            "model": car.model,
            "category": car.category
        }
    return {"error": "Car not found"}

# Address schema
class Location(BaseModel):
    formatted_address: str
    city: str
    state: str
    zip: str
    lat: float
    lng: float

@app.post("/pickup")
def pickup_address(location: Location):
    return {"message": "Pickup received", "location": location}

@app.post("/dropoff")
def dropoff_address(location: Location):
    return {"message": "Dropoff received", "location": location}

