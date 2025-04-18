from fastapi import FastAPI
from config.config import settings
from api.router import api_router

def start_server():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    app.include_router(api_router)
    return app

app = start_server()