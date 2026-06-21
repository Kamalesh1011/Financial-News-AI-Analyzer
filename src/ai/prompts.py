"""Prompt templates for financial analysis."""
from typing import Any, Dict, List


class PromptTemplates:
    """Collection of prompt templates for financial analysis."""

    SENTIMENT_SYSTEM = """You are an expert financial analyst specializing in market sentiment analysis.
Your task is to analyze financial news and provide structured sentiment assessments.

Key principles:
1. Be objective and data-driven
2. Consider both direct and indirect market impacts
3. Assess confidence based on clarity and specificity of the news
4. Consider historical context and market conditions
5. Always provide clear reasoning

Output format: JSON with the following structure:
{
    "sentiment": "bullish" | "bearish" | "neutral",
    "confidence": 0.0-1.0,
    "key_events": ["event1", "event2"],
    "reasoning": "detailed explanation",
    "impact_timeframe": "immediate" | "short_term" | "medium_term" | "long_term"
}"""

    SENTIMENT_USER = """Analyze the following financial news article for market sentiment.

Title: {title}
Summary: {summary}
Source: {source}
Published: {published_at}
Tickers Mentioned: {tickers}

Provide your analysis in the specified JSON format."""

    IMPACT_SYSTEM = """You are an expert financial impact analyst.
Your task is to identify which assets are affected by financial news and predict the direction of impact.

For each affected asset:
- Determine the direction (bullish, bearish, neutral)
- Estimate confidence (0.0-1.0)
- Classify the asset type (stock, crypto, forex, commodity, etf)
- Provide brief reasoning

Consider:
1. Direct company impacts
2. Sector/industry effects
3. Macroeconomic implications
4. Cross-asset correlations
5. Market sentiment spillovers

Output format: JSON with the following structure:
{
    "impact_score": -1.0 to 1.0,
    "risk_level": "high" | "medium" | "low",
    "reasoning": "overall analysis",
    "affected_assets": [
        {
            "symbol": "TICKER",
            "direction": "bullish" | "bearish" | "neutral",
            "confidence": 0.0-1.0,
            "asset_type": "stock" | "crypto" | "forex" | "commodity" | "etf",
            "reasoning": "specific impact reasoning"
        }
    ]
}"""

    IMPACT_USER = """Analyze the impact of the following news on financial markets.

News Title: {title}
News Summary: {summary}
Sentiment: {sentiment} (confidence: {confidence})
Key Events: {key_events}

Provide your impact analysis in the specified JSON format."""

    BATCH_SENTIMENT_SYSTEM = """You are an expert financial sentiment analyzer.
Analyze multiple news articles and provide sentiment for each.

For each article, provide:
- sentiment: bullish, bearish, or neutral
- confidence: 0.0-1.0
- key_events: list of key events mentioned
- reasoning: brief explanation

Output format: JSON array with objects for each article in the same order."""

    BATCH_SENTIMENT_USER = """Analyze the sentiment of the following {count} financial news articles.

{articles_text}

Provide your analysis as a JSON array, one object per article, in the same order."""

    SUMMARY_SYSTEM = """You are a financial news summarizer.
Create concise, actionable summaries of financial news suitable for traders and investors.
Focus on:
1. Key facts and numbers
2. Market implications
3. Action items or things to watch
4. Risk factors

Keep summaries under 100 words."""

    SUMMARY_USER = """Summarize the following financial news article:

Title: {title}
Content: {content}

Provide a concise, actionable summary."""

    @classmethod
    def format_sentiment_prompt(cls, article: Dict[str, Any]) -> List[Dict[str, str]]:
        """Format sentiment analysis prompt."""
        return [
            {"role": "system", "content": cls.SENTIMENT_SYSTEM},
            {"role": "user", "content": cls.SENTIMENT_USER.format(
                title=article.get("title", ""),
                summary=article.get("summary", ""),
                source=article.get("source", ""),
                published_at=article.get("published_at", ""),
                tickers=", ".join(article.get("tickers", [])),
            )},
        ]

    @classmethod
    def format_impact_prompt(
        cls,
        article: Dict[str, Any],
        sentiment: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Format impact analysis prompt."""
        return [
            {"role": "system", "content": cls.IMPACT_SYSTEM},
            {"role": "user", "content": cls.IMPACT_USER.format(
                title=article.get("title", ""),
                summary=article.get("summary", ""),
                sentiment=sentiment.get("sentiment", "neutral"),
                confidence=sentiment.get("confidence", 0.5),
                key_events=", ".join(sentiment.get("key_events", [])),
            )},
        ]

    @classmethod
    def format_batch_sentiment_prompt(cls, articles: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format batch sentiment analysis prompt."""
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"\n--- Article {i} ---\n"
            articles_text += f"Title: {article.get('title', '')}\n"
            articles_text += f"Summary: {article.get('summary', '')}\n"
            articles_text += f"Tickers: {', '.join(article.get('tickers', []))}\n"

        return [
            {"role": "system", "content": cls.BATCH_SENTIMENT_SYSTEM},
            {"role": "user", "content": cls.BATCH_SENTIMENT_USER.format(
                count=len(articles),
                articles_text=articles_text,
            )},
        ]

    @classmethod
    def format_summary_prompt(cls, article: Dict[str, Any]) -> List[Dict[str, str]]:
        """Format summary prompt."""
        return [
            {"role": "system", "content": cls.SUMMARY_SYSTEM},
            {"role": "user", "content": cls.SUMMARY_USER.format(
                title=article.get("title", ""),
                content=article.get("summary", "") or article.get("content", ""),
            )},
        ]