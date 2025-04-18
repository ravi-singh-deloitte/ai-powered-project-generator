from api.routes import upload
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(upload.router, prefix="", tags=["upload"])