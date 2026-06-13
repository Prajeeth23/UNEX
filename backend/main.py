from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.api.routes import router, voice_controller
from config.logging_config import setup_logging
from src.memory.database import init_db
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger("UNEX")
    logger.info("Initializing Database...")
    init_db()
    logger.info("Starting Voice Controller...")
    voice_controller.start()
    
    logger.info("Database Initialized. Starting up...")
    yield
    logger.info("Shutting down Voice Controller...")
    voice_controller.stop()
    logger.info("Shutting down...")

app = FastAPI(
    title="UNEX API",
    description="Backend API for UNEX Local Assistant",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "UNEX API is running"}
