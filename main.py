from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os

DATABASE_URL = "postgresql://car_user:FFiCalDwRyZwiJKt5hjpsOvAaiL6sBoL@dpg-d1de9eer433s73f6bt50-a.oregon-postgres.render.com/car_api_l6s0"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    make = Column(String)
    model = Column(String)
    category = Column(String)

Base.metadata.create_all(bind=engine)

# ✅ Load CSV into PostgreSQL (only once)
def load_data_once():
    session = SessionLocal()
    car_count = session.query(Car).count()
    if car_count == 0:
        print("Loading car data from CSV...")
        df = pd.read_csv("cars.csv")
        for _, row in df.iterrows():
            car = Car(
                year=int(row['year']),
                make=str(row['make']),
                model=str(row['model']),
                category=str(row['category'])
            )
            session.add(car)
        session.commit()
        print("Car data loaded.")
    else:
        print("Car data already exists. Skipping load.")
    session.close()

# Run the data loader once at startup
load_data_once()

app = FastAPI()

@app.get("/cars")
def get_cars():
    session = SessionLocal()
    cars = session.query(Car).limit(50).all()
    session.close()
    return [{"make": c.make, "model": c.model, "year": c.year, "category": c.category} for c in cars]
