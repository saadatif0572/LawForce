import time
import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.db.session import init_db
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.chats import router as chats_router
from backend.app.api.v1.sources import router as sources_router
from backend.app.api.v1.feedback import router as feedback_router
from backend.app.api.v1.admin import router as admin_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("lawverse.main")

app = FastAPI(
    title="LAWVERSE API",
    description="Professional Pakistani Legal Information & Research Assistant RAG Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    settings.FRONTEND_ORIGIN
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if settings.APP_ENV == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID and Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing the legal inquiry."}
    )

# Startup Event
@app.on_event("startup")
def on_startup():
    logger.info("Initializing database schemas...")
    init_db()
    logger.info("LawForce Backend API initialized successfully.")

# Include API v1 Routers
api_v1_prefix = "/api/v1"
app.include_router(health_router, prefix=api_v1_prefix)
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(chat_router, prefix=api_v1_prefix)
app.include_router(chats_router, prefix=api_v1_prefix)
app.include_router(sources_router, prefix=api_v1_prefix)
app.include_router(feedback_router, prefix=api_v1_prefix)
app.include_router(admin_router, prefix=api_v1_prefix)

@app.get("/")
def root():
    return {
        "service": "LawForce API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "verified_corpus_target": 500
    }
