"""Роутер FastAPI"""

from fastapi import APIRouter
from app.api.api_v1.endpoints import users, usercontacts, userhistory

api_router = APIRouter()

api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(usercontacts.router, prefix='/usercontacts', tags=['usercontacts'])
api_router.include_router(userhistory.router, prefix='/userhistory', tags=['userhistory'])
