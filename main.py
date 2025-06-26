from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
import pandas as pd

# Database
DATABASE_URL = "postgresql://car_user:FFiCalDwRyZwiJKt5hjpsOvAaiL6sBoL@dpg-d1de9eer433s73f6bt50-a.oregon-postgres.render.com/car_api_l6s0"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Tables
class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    make = Column(String)
    model = Column(String)
    category = Column(String)

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True, index=True)
    pickup = Column(String)
    dropoff = Column(String)
    transport_type = Column(String)
    year = Column(String)
    make = Column(String)
    model = Column(String)
    operable = Column(String)
    email = Column(String)
    phone = Column(String)
    date = Column(String)  # Changed from 'shipping_date' to 'date' to match plugin

Base.metadata.create_all(bind=engine)

# Load car data from Excel (only once)
def load_data_once():
    db = SessionLocal()
    if not db.query(Car).first():
        df = pd.read_excel("cars.xlsx")
        for _, row in df.iterrows():
            db.add(Car(
                year=int(row['year']),
                make=str(row['make']),
                model=str(row['model']),
                category=str(row['category'])
            ))
        db.commit()
    db.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_data_once()

@app.get("/")
def home():
    return {"message": "API Running"}

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

class QuoteSubmission(BaseModel):
    pickup: str
    dropoff: str
    transport_type: str
    year: str
    make: str
    model: str
    operable: str
    email: str
    phone: str
    date: str  # Changed from 'shipping_date' to 'date'

@app.post("/submit-quote")
def submit_quote(quote: QuoteSubmission):
    db = SessionLocal()
    new_quote = Quote(**quote.dict())
    db.add(new_quote)
    db.commit()
    db.close()
    return {"message": "Quote submitted", "status": "ok"}

