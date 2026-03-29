import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.repositories.user_trainer_package_repository import UserTrainerPackageRepository

logger = logging.getLogger(__name__)


async def _expired_trainer_packages_worker():
    while True:
        db = SessionLocal()
        try:
            repo = UserTrainerPackageRepository(db)
            repo.finish_expired_active_packages()
        except Exception:
            db.rollback()
            logger.exception("Failed to finish expired trainer packages")
        finally:
            db.close()
        await asyncio.sleep(24 * 60 * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.avatar_path.mkdir(parents=True, exist_ok=True)
    settings.gym_path.mkdir(parents=True, exist_ok=True)

    app.mount("/avatars", StaticFiles(directory=settings.avatar_path), name="avatars")
    app.mount("/gyms", StaticFiles(directory=settings.gym_path), name="gyms")
    app.state.expired_trainer_packages_worker = asyncio.create_task(_expired_trainer_packages_worker())
    yield
    app.state.expired_trainer_packages_worker.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await app.state.expired_trainer_packages_worker

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
