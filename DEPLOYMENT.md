# Vercel Deployment Guide

## Quick Deploy

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy (from project root)
vercel
```

## Environment Variables (Set in Vercel Dashboard)

### Required
| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DB` | Database name (default: `finnews`) |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI analysis |
| `JWT_SECRET` | Secret for JWT authentication |

### News & Market Data
| Variable | Description |
|----------|-------------|
| `FINNHUB_API_KEY` | Finnhub API key |
| `NEWSAPI_API_KEY` | NewsAPI key |

### AI Services
| Variable | Description |
|----------|-------------|
| `NIM_API_KEY` | NVIDIA NIM API key |

### Notifications (Optional)
| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat ID |
| `SMTP_USER` | Email sender |
| `SMTP_PASS` | Email password |
| `ALERT_EMAIL_TO` | Recipient email |

## Production URL

After deployment, set `VITE_API_BASE_URL` to your Vercel deployment URL:
- Go to Vercel Dashboard → Settings → Environment Variables
- Add `VITE_API_BASE_URL` = `https://your-project.vercel.app`
- Redeploy

## Architecture

```
your-project.vercel.app
├── /api/*          → FastAPI (Python serverless)
│   ├── /api/news
│   ├── /api/market
│   ├── /api/sentiment
│   ├── /api/impact
│   ├── /api/alerts
│   ├── /api/auth/*
│   └── /api/cron/*
└── /*              → React (static files)
    ├── /index.html
    └── /assets/*
```

## Local Development

```bash
# Backend
cd project root
pip install -r requirements.txt
uvicorn src.api.routes:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Build Fails
- Ensure Node.js >= 18
- Run `cd frontend && npm install` locally first

### API Returns 404
- Check `VITE_API_BASE_URL` is set correctly
- Ensure MongoDB Atlas IP whitelist includes Vercel

### CORS Errors
- Backend already configured with `allow_origins=["*"]`
- If issues persist, add your Vercel URL to CORS origins
