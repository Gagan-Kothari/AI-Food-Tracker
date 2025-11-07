from fastapi import FastAPI # type: ignore (venv)
from app.routes import routes
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Ensure tables exist in the configured DATABASE_URL
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # If migration tool manages schema, ignore
    pass
app.include_router(routes.router)

# CORS Configuration
# For production, allow all origins to prevent CORS errors
# Note: When using allow_origins=["*"], allow_credentials must be False
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")

# Default origins including the Vercel frontend
default_origins = [
    "https://ai-food-tracker-eight.vercel.app",
    "https://ai-food-tracker.vercel.app",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]

if ALLOWED_ORIGINS_ENV:
    # Use specific origins from environment variable
    env_origins = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",") if origin.strip()]
    origins = list(set(default_origins + env_origins))  # Combine and remove duplicates
    allow_credentials = True
else:
    # Default: Allow all origins (for deployment compatibility)
    # This prevents CORS errors from any frontend domain
    origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],  # Allows all methods: POST, GET, OPTIONS, etc.
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message" : "App running"}