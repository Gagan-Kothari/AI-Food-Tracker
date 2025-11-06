# Railway Deployment Guide

## Project Structure Analysis

- **FastAPI App**: `app/main.py` (entry point: `app.main:app`)
- **Dependencies**: `requirements.txt` (15 packages)
- **Database**: PostgreSQL (via `DATABASE_URL` env var)
- **Python Version**: 3.13

## ✅ Clean Setup Created

### Files Created:
1. **Dockerfile** - Complete, production-ready Docker configuration
2. **.dockerignore** - Excludes unnecessary files from Docker build

### Files Removed:
- ❌ railpack.json (wasn't working)
- ❌ Procfile (was causing Railpack detection)
- ❌ runtime.txt (not needed with Dockerfile)

## 🚀 Deployment Steps

### Option 1: Use Dockerfile (RECOMMENDED - Most Reliable)

1. **In Railway Dashboard:**
   - Service → Settings → Deploy
   - **Builder**: Select **"Dockerfile"**
   - **Start Command**: Leave empty (Dockerfile CMD handles it)
   - **Build Command**: Leave empty (Dockerfile RUN handles it)

2. **Set Environment Variables:**
   - `DATABASE_URL` - Your PostgreSQL connection string
   - Any other API keys (SPOONACULAR_API_KEY, etc.)

3. **Deploy:**
   - Commit and push, or click "Redeploy"

### Option 2: Use Railpack (If you prefer)

1. **In Railway Dashboard:**
   - Service → Settings → Deploy
   - **Builder**: Select **"Railpack"** or **"Auto-detect"**
   - **Build Command**: Set to:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**: Set to:
     ```bash
     python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

2. **Set Environment Variables** (same as above)

## ✅ What Success Looks Like

### With Dockerfile:
```
Step 1/8 : FROM python:3.13-slim
Step 2/8 : WORKDIR /app
Step 3/8 : COPY requirements.txt .
Step 4/8 : RUN pip install --upgrade pip && pip install -r requirements.txt
Collecting fastapi==0.115.3
Collecting uvicorn[standard]==0.34.0
...
Successfully installed fastapi-0.115.3 uvicorn-0.34.0 ...
Build time: 60+ seconds
```

### With Railpack (if Build Command set):
```
Railpack 0.10.0
↳ Detected Python
▸ build
$ pip install --upgrade pip && pip install -r requirements.txt
Collecting fastapi==0.115.3
...
Successfully installed ...
Build time: 60+ seconds
```

## 🔍 Verification

After deployment, check:
1. **Build logs** show dependency installation
2. **Deploy logs** show: `INFO: Uvicorn running on http://0.0.0.0:8000`
3. **API responds** at Railway's public URL
4. **No errors** about missing modules

## 📝 Key Points

- **Dockerfile is most reliable** - Guarantees dependencies are installed
- **Railpack requires Build Command in dashboard** - Config files alone don't work
- **Environment variables must be set** - Especially `DATABASE_URL`
- **Start command**: `app.main:app` (not `main.py`)

