from fastapi import FastAPI # type: ignore (venv)
from app.routes import routes
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Ensure tables exist in the configured DATABASE_URL
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # If migration tool manages schema, ignore
    pass
app.include_router(routes.router)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Using ["*"] to allow all for deployment on Vercel
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods: POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message" : "App running"}