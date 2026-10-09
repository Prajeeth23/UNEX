from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.api.routes import router, voice_controller
from config.logging_config import setup_logging
from src.memory.database import init_db
import logging
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger("UNEX")
    logger.info("Initializing Database...")
    init_db()
    logger.info("Starting Voice Controller...")
    voice_controller.start()
    
    logger.info("Database Initialized. Starting up...")
    
    # Launch Standalone Native Desktop GUI Window (App Mode)
    from src.gui.app_window import launch_gui_window
    launch_gui_window()
    
    yield
    logger.info("Shutting down Voice Controller...")
    voice_controller.stop()
    logger.info("Shutting down...")

app = FastAPI(
    title="UNEX OS API & Mission Control",
    description="Backend API and Dashboard for UNEX Local Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Mount static frontend dashboard
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/dashboard", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/api/status")
async def api_status():
    return {"status": "online", "mode": "production"}

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard/")

