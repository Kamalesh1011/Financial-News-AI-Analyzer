# Financial News AI Analyzer

AI-powered financial news analysis with real-time market data, sentiment scoring, and automated alerts.

## Features

- **Real-time News Collection** from Finnhub and NewsAPI
- **Market Data** from Finnhub, CoinGecko, and Binance
- **AI Sentiment Analysis** via OpenRouter and NIM (NVIDIA)
- **Impact Mapping** linking news to affected assets
- **Automated Alerts** via Telegram and Email
- **Interactive Dashboard** built with Streamlit

## Architecture

```
News APIs → Market Data → AI Analyzer → Impact Mapper → Dashboard + Alerts
     ↓            ↓            ↓              ↓              ↓
  Finnhub     CoinGecko    OpenRouter     Rule Engine    Streamlit
  NewsAPI     Binance      NIM            + LLM          Telegram
                                                  Email
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Vercel) |
| Dashboard | Streamlit (Streamlit Cloud) |
| Database | MongoDB Atlas (Free M0) |
| LLM | OpenRouter + NIM |
| Market Data | Finnhub + CoinGecko + Binance |
| News | Finnhub + NewsAPI |
| Alerts | Telegram Bot + SMTP |

## Quick Start

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/financial-news-analyzer.git
   cd financial-news-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

5. **Run locally**
   ```bash
   make run-local
   ```

## API Keys Required

| Service | Free Tier | Get Key |
|---------|-----------|---------|
| Finnhub | 60 req/min | [finnhub.io](https://finnhub.io) |
| NewsAPI | 100 req/day | [newsapi.org](https://newsapi.org) |
| CoinGecko | 100 req/min | [coingecko.com](https://coingecko.com) |
| OpenRouter | Pay-per-use | [openrouter.ai](https://openrouter.ai) |
| NIM | Pay-per-use | [build.nvidia.com](https://build.nvidia.com) |
| Telegram | Unlimited | [@BotFather](https://t.me/BotFather) |

## Project Structure

```
financial-news-analyzer/
├── config/             # Configuration & constants
├── src/
│   ├── agents/         # Pipeline agents
│   ├── api/            # FastAPI routes & clients
│   ├── ai/             # LLM clients
│   ├── db/             # MongoDB models & repositories
│   ├── alerts/         # Alert sending
│   └── utils/          # Utilities
├── dashboard/          # Streamlit dashboard
├── tests/              # Tests
├── scripts/            # Helper scripts
└── docs/               # Documentation
```

## Deployment

### Vercel (Backend)
1. Push to GitHub
2. Import in Vercel
3. Configure environment variables
4. Deploy

### Streamlit Cloud (Dashboard)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select repo and `dashboard/app.py`
4. Configure secrets

## License

MIT