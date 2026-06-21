# API Setup Guide

## Required API Keys

### 1. Finnhub (Market Data & News)
- **Free Tier**: 60 requests/minute
- **Get Key**: https://finnhub.io/register
- **Usage**: Stock quotes, company news, market data

### 2. NewsAPI (News Aggregation)
- **Free Tier**: 100 requests/day
- **Get Key**: https://newsapi.org/register
- **Usage**: Financial news headlines, article search

### 3. CoinGecko (Crypto Data)
- **Free Tier**: 100 requests/minute (with Demo key)
- **Get Key**: https://www.coingecko.com/api/pricing
- **Usage**: Crypto prices, market cap, trending coins

### 4. OpenRouter (LLM - Primary)
- **Pricing**: Pay-per-use (~$0.01-0.03 per analysis)
- **Get Key**: https://openrouter.ai/keys
- **Usage**: Sentiment analysis, impact mapping
- **Recommended Models**: Claude 3.5 Sonnet, GPT-4o

### 5. NVIDIA NIM (LLM - Fallback)
- **Pricing**: Pay-per-use
- **Get Key**: https://build.nvidia.com
- **Usage**: Fallback LLM for sentiment analysis
- **Recommended Models**: Nemotron-3-Ultra, Llama 3.1 405B

### 6. Telegram Bot (Alerts)
- **Free**: Unlimited messages
- **Setup**:
  1. Message @BotFather on Telegram
  2. Create a new bot with `/newbot`
  3. Get bot token
  4. Send a message to your bot
  5. Get chat ID: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`

### 7. SMTP Email (Alerts)
- **Options**: Gmail, Outlook, SendGrid
- **Gmail Setup**:
  1. Enable 2-Factor Authentication
  2. Generate App Password: https://myaccount.google.com/apppasswords
  3. Use app password (not regular password)

## Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

## MongoDB Atlas Setup

1. Create free account: https://cloud.mongodb.com
2. Create M0 cluster (free tier)
3. Create database user
4. Whitelist IP addresses (0.0.0.0/0 for development)
5. Get connection string
6. Add to `.env`:
   ```
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/finnews
   ```

## Cost Estimation

| Service | Free Tier | Paid Estimate |
|---------|-----------|---------------|
| MongoDB Atlas | 512MB free | $0 (M0) |
| Finnhub | 60 req/min | $0 |
| NewsAPI | 100 req/day | $0 |
| CoinGecko | 100 req/min | $0 |
| OpenRouter | - | ~$5-15/mo |
| NIM | - | ~$5-15/mo |
| Telegram | Unlimited | $0 |
| Email | SMTP | $0 |
| **Total** | | **~$10-30/mo** |