from app.main import app as fastapi_app

# Expose the FastAPI ASGI app to Vercel Python runtime
app = fastapi_app


