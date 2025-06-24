from fastapi import FastAPI

app = FastAPI()

cars = [
    {"make": "Toyota", "model": "Camry", "category": "sedan"},
    {"make": "Ford", "model": "Escape", "category": "suv"},
    {"make": "Honda", "model": "Civic", "category": "compact"},
]

@app.get("/cars")
def get_cars():
    return [{"make": c["make"], "model": c["model"]} for c in cars]

@app.get("/cars/internal")
def get_internal():
    return cars
