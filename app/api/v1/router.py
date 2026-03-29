from fastapi import APIRouter

from app.api.v1.endpoints import auth, avatar, booking, client_assets, client_service, gym, progress, review, service, subscription, trainer_slot

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
    client_assets.router,
    prefix="/clients",
    tags=["client services"]
)

api_router.include_router(
    booking.router,
    prefix="/clients",
    tags=["client bookings"]
)

api_router.include_router(
    progress.router,
    prefix="/clients",
    tags=["client progress"]
)

api_router.include_router(
    review.router,
    tags=["reviews"]
)

api_router.include_router(
    subscription.router,
    prefix="/subscriptions",
    tags=["subscriptions"]
)

api_router.include_router(
    trainer_slot.router,
    prefix="/trainers",
    tags=["trainer slots"]
)
