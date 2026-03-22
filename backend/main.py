from fastapi import FastAPI
from routes import health, pipeline, household, foodbank

app = FastAPI()

app.include_router(health.router)
app.include_router(pipeline.router)
app.include_router(household.router)
app.include_router(foodbank.router)