# Railway Configuration Guide

## ✅ Root Directory Setting

**Root Directory: `/app` or `app`**

- Set **Root Directory** to **`app`** in Railway dashboard
- Railway will change working directory to the `app/` folder
- All commands will run from within the `app/` directory

## ✅ Startup Code

**Created in `app/start.py`** - This is your startup script.

### What `app/start.py` does:
- Reads `PORT` environment variable from Railway
- Starts uvicorn with your FastAPI app
- Handles the port correctly (no more `$PORT` expansion issues)
- Uses `main:app` since we're already in the app/ directory

## 🚀 Railway Dashboard Settings

### 1. Root Directory
- Set to: **`app`** (the folder name, not `/app`)
- Railway will run all commands from the `app/` directory

### 2. Build Command
- Set to: `pip install --upgrade pip && pip install -r requirements.txt`
- This installs all dependencies from `app/requirements.txt`

### 3. Start Command
- Set to: `python start.py`
- This runs `app/start.py` which handles PORT correctly

### 4. Environment Variables
- `DATABASE_URL` - Your PostgreSQL connection string
- Any other API keys you need

## 📁 Project Structure

```
your-repo-root/
├── app/                  ← Railway root directory (set to "app")
│   ├── start.py         ← Startup script (created here)
│   ├── requirements.txt ← Dependencies (copied here)
│   ├── main.py          ← FastAPI app
│   ├── routes/
│   ├── crud/
│   └── ...
└── ...
```

## ✅ Summary

- **Root Directory**: `app` (the folder name)
- **Start Command**: `python start.py`
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`

The `app/start.py` script handles everything!

