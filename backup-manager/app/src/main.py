from fastapi import FastAPI
from app.src.api.routes import router

app = FastAPI()
app.include_router(router)