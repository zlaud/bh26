from fastapi import FastAPI
from routes import health, pipeline

app = FastAPI()

app.include_router(health.router)
app.include_router(pipeline.router)