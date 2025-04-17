from fastapi import FastAPI
from core.config import settings
from api.base import api_router

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    app.include_router(api_router)
    return app


app = start_application()