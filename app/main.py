from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.avatar_path.mkdir(parents=True, exist_ok=True)
    settings.gym_path.mkdir(parents=True, exist_ok=True)

    app.mount("/avatars", StaticFiles(directory=settings.avatar_path), name="avatars")
    app.mount("/gyms", StaticFiles(directory=settings.gym_path), name="gyms")
    yield

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