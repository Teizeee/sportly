from fastapi import APIRouter

from app.api.v1.endpoints import auth, avatar, gym

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    avatar.router,
    prefix="/avatars",
    tags=["avatars"]
)

api_router.include_router(
    gym.router,
    prefix="/gyms",
    tags=["gyms"]
)