from fastapi import APIRouter

from app.api.v1.endpoints import auth, avatar, client_service, gym, service, subscription

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

api_router.include_router(
    service.router,
    prefix="/gyms",
    tags=["gym services"]
)

api_router.include_router(
    client_service.router,
    prefix="/gyms",
    tags=["client services"]
)

api_router.include_router(
    subscription.router,
    prefix="/subscriptions",
    tags=["subscriptions"]
)
