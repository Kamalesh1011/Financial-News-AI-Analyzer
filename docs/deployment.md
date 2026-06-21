# Deployment Guide

## Overview

The Financial News Analyzer is split into two deployments:
1. **Vercel** - FastAPI backend with cron jobs
2. **Streamlit Cloud** - Interactive dashboard

## 1. Vercel Deployment (Backend)

### Prerequisites
- Vercel account (free tier works)
- GitHub repository with the project

### Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/financial-news-analyzer.git
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com
   - Click "Add New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Configure Environment Variables**
   - In Vercel dashboard, go to Settings > Environment Variables
   - Add all variables from `.env.example`:
     - `MONGODB_URI`
     - `FINNHUB_API_KEY`
     - `NEWSAPI_API_KEY`
     - `OPENROUTER_API_KEY`
     - `NIM_API_KEY`
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHAT_ID`
     - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
     - `ALERT_EMAIL_TO`

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Cron jobs will run automatically based on `vercel.json`

### Cron Jobs

| Path | Schedule | Description |
|------|----------|-------------|
| `/api/cron/collect-news` | Every 5 min | Collect news from APIs |
| `/api/cron/collect-market` | Every 2 min | Collect market data |
| `/api/cron/analyze-sentiment` | Every 5 min | Analyze sentiment |
| `/api/cron/check-alerts` | Every 1 min | Check and send alerts |

### API Endpoints

Once deployed, your API will be available at:
- Base URL: `https://your-project.vercel.app`
- API Docs: `https://your-project.vercel.app/docs`
- Health Check: `https://your-project.vercel.app/health`

## 2. Streamlit Cloud Deployment (Dashboard)

### Prerequisites
- Streamlit Cloud account (free)
- GitHub repository (same as Vercel)

### Steps

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Sign in with GitHub

2. **Create New App**
   - Click "New app"
   - Select your repository
   - Set main file path: `dashboard/app.py`
   - Set Python version: 3.11

3. **Configure Secrets**
   - In app settings, go to "Secrets"
   - Add the following:
     ```toml
     API_BASE_URL = "https://your-project.vercel.app"
     ```

4. **Deploy**
   - Click "Deploy"
   - Streamlit Cloud will build and deploy

### Dashboard Features

- News feed with sentiment badges
- Market data panels
- Impact analysis visualization
- Alert history
- Watchlist management

## 3. Local Development

### Prerequisites
- Python 3.11+
- MongoDB Atlas account (or local MongoDB)

### Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Initialize Database**
   ```bash
   python scripts/init_db.py
   python scripts/seed_watchlist.py
   ```

4. **Run Locally**
   ```bash
   # Run all services
   make run-local

   # Or run individually
   make run-api        # API server on port 8000
   make run-dashboard  # Dashboard on port 8501
   ```

5. **Access Services**
   - API: http://localhost:8000
   - Dashboard: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## 4. Docker Deployment (Optional)

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    command: uvicorn src.api.routes:app --host 0.0.0.0 --port 8000

  dashboard:
    build: .
    ports:
      - "8501:8501"
    env_file: .env
    command: streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

### Run with Docker Compose
```bash
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check `MONGODB_URI` is correct
   - Ensure IP whitelist includes your IP
   - Verify database user credentials

2. **API Rate Limits**
   - Finnhub: 60 req/min free tier
   - NewsAPI: 100 req/day free tier
   - Consider upgrading if hitting limits

3. **LLM Errors**
   - Verify API keys are valid
   - Check account balance for OpenRouter/NIM
   - Review rate limits

4. **Telegram Alerts Not Sending**
   - Verify bot token is correct
   - Ensure bot is added to chat
   - Check chat ID is correct

### Logs

- Vercel: Check function logs in dashboard
- Streamlit: Check app logs in Streamlit Cloud
- Local: Check console output

## Monitoring

### Health Checks

```bash
# Check API health
curl https://your-project.vercel.app/health

# Check MongoDB connection
curl https://your-project.vercel.app/ready

# Get database stats
curl https://your-project.vercel.app/api/stats
```

### Metrics

The API exposes several monitoring endpoints:
- `/health` - Service health status
- `/ready` - Readiness check
- `/api/stats` - Database statistics
- `/api/alerts` - Alert history