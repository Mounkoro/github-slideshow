from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .db import Base, engine
from .routers import auth as auth_router
from .routers import accounts as accounts_router
from .routers import admin as admin_router
from pathlib import Path
import logging

app = FastAPI(title="Bank Manager API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:  # log but do not crash to allow health check before DB is ready
        logging.exception("Database initialization failed. Check DB connectivity and settings.")


app.include_router(auth_router.router)
app.include_router(accounts_router.router)
app.include_router(admin_router.router)
