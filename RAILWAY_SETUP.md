# Railway Deployment Setup Guide

## Prerequisites
- GitHub repository with your code
- Railway account (railway.app)
- PostgreSQL database (Railway provides this)

## Step 1: Ensure Required Files Are in Repository Root

Make sure these files are in your repository root and committed to git:

### Required Files:
1. ✅ `Dockerfile` - For building your application
2. ✅ `requirements.txt` - Python dependencies
3. ✅ `app/main.py` - Your FastAPI application entry point
4. ✅ `.env` - Environment variables (add to .gitignore, set in Railway dashboard)

### Optional but Recommended:
- `Procfile` - Alternative start command (not needed if using Dockerfile)
- `runtime.txt` - Python version specification
- `.gitignore` - To exclude unnecessary files

## Step 2: Verify Dockerfile

Your `Dockerfile` should look like this:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start command (PORT will be set by Railway)
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## Step 3: Create New Railway Project

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will detect your Dockerfile automatically

## Step 4: Configure Service Settings

### In Railway Dashboard:

1. **Click on your service** → **Settings**

2. **Build Settings:**
   - **Builder:** Select **"Dockerfile"** (NOT Railpack)
   - **Dockerfile Path:** Leave empty (or `Dockerfile` if in root)

3. **Deploy Settings:**
   - **Start Command:** Leave empty (Dockerfile CMD will be used)
   - Or set to: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Step 5: Set Environment Variables

In Railway Dashboard → Your Service → Variables:

Add these environment variables:

```
DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname
```

**To get DATABASE_URL:**
1. Create a PostgreSQL service in Railway
2. Go to PostgreSQL service → Variables
3. Copy the `DATABASE_URL` value
4. Add it to your main service variables

### Other Environment Variables (if needed):
- `SPOONACULAR_API_KEY` - For recipe API (if using)
- Any other API keys or secrets your app needs

## Step 6: Deploy

1. Railway will automatically deploy when you:
   - Push to your main branch (if connected to GitHub)
   - Or click **"Deploy"** in the dashboard

2. **Monitor the build logs:**
   - You should see:
     ```
     Step 4/7 : COPY requirements.txt .
     Step 5/7 : RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
     Collecting fastapi==0.115.3
     Collecting uvicorn[standard]==0.34.0
     ...
     Successfully installed ...
     ```

## Step 7: Verify Deployment

1. **Check build logs** - Should show successful dependency installation
2. **Check deployment logs** - Should show:
   ```
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```
3. **Test your API** - Railway provides a public URL

## Troubleshooting

### If build fails with "No module named uvicorn":
- ✅ Ensure Builder is set to "Dockerfile" (NOT Railpack)
- ✅ Verify `requirements.txt` is in repository root
- ✅ Check that `requirements.txt` is committed to git

### If requirements.txt not found:
- ✅ Verify file is in repository root
- ✅ Check `.gitignore` doesn't exclude it
- ✅ Ensure file is committed: `git add requirements.txt && git commit -m "Add requirements"`

### If database connection fails:
- ✅ Verify `DATABASE_URL` is set in Railway variables
- ✅ Check PostgreSQL service is running
- ✅ Ensure database URL format is correct

### If still using Railpack:
- ✅ Delete the service and recreate
- ✅ Or manually set Builder to "Dockerfile" in settings
- ✅ Remove any `railpack.json` or `railway.json` that might force Railpack

## Quick Checklist

Before deploying, verify:
- [ ] `Dockerfile` exists in root directory
- [ ] `requirements.txt` exists and is committed
- [ ] `app/main.py` exists (your FastAPI app)
- [ ] Builder is set to "Dockerfile" in Railway
- [ ] `DATABASE_URL` environment variable is set
- [ ] All code is pushed to GitHub
- [ ] Railway is connected to your GitHub repo

## File Structure Should Look Like:

```
your-repo/
├── Dockerfile          ← Required
├── requirements.txt    ← Required
├── railway.json        ← Optional (can help force Dockerfile)
├── .gitignore
├── app/
│   ├── main.py        ← Your FastAPI app
│   ├── routes/
│   ├── crud/
│   └── ...
└── ...
```

## Success Indicators

✅ Build logs show: "Successfully installed fastapi uvicorn ..."
✅ Deployment logs show: "Uvicorn running on http://0.0.0.0:8000"
✅ API responds at Railway's public URL
✅ No "No module named uvicorn" errors

