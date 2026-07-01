# Vercel Deployment Guide

## Architecture

```
your-project.vercel.app
├── /api/*          → FastAPI (Python serverless via api/index.py)
│   ├── /api/news
│   ├── /api/market
│   ├── /api/sentiment
│   ├── /api/impact
│   ├── /api/alerts
│   ├── /api/auth/*
│   ├── /api/watchlist
│   ├── /api/correlation
│   ├── /api/portfolio/risk
│   ├── /api/backtest
│   └── /api/cron/*
├── /health         → FastAPI health check
├── /ready          → FastAPI readiness check
└── /*              → React SPA (static files from frontend/dist/)
```

## Quick Deploy

```bash
# 1. Install Vercel CLI (if not installed)
npm i -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy (from project root D:\dubai_project2)
vercel

# 4. When prompted:
#    - Set up and deploy? → Y
#    - Which scope? → Select your account
#    - Link to existing project? → N
#    - Project name? → finnews-ai (or your choice)
#    - Directory where code is located? → ./

# 5. Deploy to production
vercel --prod
```

## Environment Variables (Set in Vercel Dashboard)

Go to **Vercel Dashboard → your project → Settings → Environment Variables**

### Required
| Variable | Value | Description |
|----------|-------|-------------|
| `MONGODB_URI` | `mongodb+srv://...` | MongoDB Atlas connection string |
| `MONGODB_DB` | `finnews` | Database name |
| `JWT_SECRET` | `<random-secret>` | Secret for JWT auth (generate with `openssl rand -hex 32`) |

### API Keys (at least one LLM provider needed)
| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key for AI analysis |
| `FINNHUB_API_KEY` | Finnhub stock/crypto data API key |
| `NEWSAPI_API_KEY` | NewsAPI key |
| `NIM_API_KEY` | NVIDIA NIM API key (optional fallback) |

### Notifications (Optional)
| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat ID |
| `SMTP_USER` | Email sender address |
| `SMTP_PASS` | Email app password |
| `ALERT_EMAIL_TO` | Recipient email address |

### Frontend (Important!)
| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_BASE_URL` | *(leave empty)* | Must be empty so frontend calls `/api/*` on same domain |

**Do NOT set `VITE_API_BASE_URL` to a full URL.** Leave it empty. The frontend will use relative paths (`/api/news`) which Vercel routes to the Python backend on the same domain.

## Local Development

```bash
# Backend (terminal 1)
cd D:\dubai_project2
pip install -r requirements.txt
uvicorn src.api.routes:app --reload --port 8000

# Frontend (terminal 2)
cd D:\dubai_project2\frontend
npm install
npm run dev
# Opens at http://localhost:5000
```

## What Changed for Vercel

### Backend Changes
- **`api/index.py`**: New entry point that adds project root to `sys.path` so imports like `config.settings`, `src.db.*` resolve correctly
- **`src/db/mongodb.py`**: Lazy connection (no lifespan manager) — connects on first DB call, reuses connection across serverless invocations
- **`src/db/repositories.py`**: All `self.collection` replaced with `await self._get_collection()` for lazy connection
- **`config/settings.py`**: All fields have defaults so the app starts without a `.env` file (Vercel uses dashboard env vars)
- **`requirements-api.txt`**: Lean dependency list excluding unused packages (streamlit, plotly, pandas)

### Frontend Changes
- **`VITE_API_BASE_URL`**: Set to empty string `""` in `vercel.json` so frontend calls `/api/*` on same origin

## How It Works

1. Vercel detects `vercel.json` in project root
2. **Python build**: `api/index.py` is built with `@vercel/python`, bundling `config/` and `src/` via `includeFiles`
3. **Frontend build**: `frontend/package.json` triggers `npm install && npm run build`, outputting to `frontend/dist/`
4. **Routing**: `/api/*` requests go to the Python serverless function, everything else serves the React SPA
5. **Crons**: 5 cron jobs run on schedule, hitting `/api/cron/*` endpoints to run the AI agents

## MongoDB Atlas Setup

1. Create a free cluster at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create a database user with read/write access
3. Whitelist IP addresses: Add `0.0.0.0/0` (allow all) for Vercel serverless
4. Copy the connection string: `mongodb+srv://<user>:<password>@cluster.mongodb.net/finnews?retryWrites=true&w=majority`
5. Set as `MONGODB_URI` in Vercel dashboard

## Troubleshooting

### Build Fails
- Ensure Node.js >= 18 locally
- Run `cd frontend && npm install` locally first to verify

### API Returns 404
- Check that `VITE_API_BASE_URL` is **empty** in Vercel env vars
- Redeploy after changing env vars

### CORS Errors
- Backend has `allow_origins=["*"]` — should work
- If issues persist, set CORS origins to your Vercel URL

### MongoDB Connection Fails
- Ensure MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- Verify connection string is correct in Vercel env vars
- Check MongoDB Atlas cluster is running

### Cold Start Slow
- First request after idle may take 5-10s (serverless cold start)
- Subsequent requests are fast (connection reused)
- MongoDB connection pools: `minPoolSize=0` for serverless compatibility
