"""
Stock Data Service - Fetches real-time data from Yahoo Finance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from cachetools import TTLCache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for stock data (5 minutes TTL)
stock_cache = TTLCache(maxsize=100, ttl=300)


class StockService:
    """
    Service for fetching stock data from Yahoo Finance
    """
    
    POPULAR_STOCKS = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "GOOGL", "name": "Alphabet Inc."},
        {"symbol": "AMZN", "name": "Amazon.com Inc."},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "META", "name": "Meta Platforms Inc."},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
        {"symbol": "V", "name": "Visa Inc."},
        {"symbol": "WMT", "name": "Walmart Inc."},
        {"symbol": "JNJ", "name": "Johnson & Johnson"},
        {"symbol": "NFLX", "name": "Netflix Inc."},
    ]
    
    @staticmethod
    def get_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed stock information
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with stock information
        """
        cache_key = f"info_{symbol}"
        if cache_key in stock_cache:
            return stock_cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            stock_info = {
                "symbol": symbol,
                "name": info.get("longName", info.get("shortName", symbol)),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "country": info.get("country", "N/A"),
                "website": info.get("website", "N/A"),
                "description": info.get("longBusinessSummary", ""),
                "marketCap": info.get("marketCap", 0),
                "marketCapFormatted": StockService._format_market_cap(
                    info.get("marketCap", 0)
                ),
                "peRatio": info.get("forwardPE", info.get("trailingPE", 0)),
                "dividendYield": info.get("dividendYield", 0),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0),
                "avgVolume": info.get("averageVolume", 0),
                "currency": info.get("currency", "USD")
            }
            
            stock_cache[cache_key] = stock_info
            return stock_info
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_current_price(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current stock price and daily change
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with current price data
        """
        cache_key = f"price_{symbol}"
        if cache_key in stock_cache:
            return stock_cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get today's data
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            price_data = {
                "symbol": symbol,
                "price": round(current_price, 2),
                "previousClose": round(previous_close, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2),
                "volume": int(hist['Volume'].iloc[-1]),
                "high": round(float(hist['High'].iloc[-1]), 2),
                "low": round(float(hist['Low'].iloc[-1]), 2),
                "open": round(float(hist['Open'].iloc[-1]), 2),
                "timestamp": datetime.now().isoformat()
            }
            
            stock_cache[cache_key] = price_data
            return price_data
            
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_historical_data(
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[Dict[str, Any]]:
        """
        Get historical stock data
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            interval: Data interval (1d, 1wk, 1mo)
            
        Returns:
            Dictionary with historical data
        """
        cache_key = f"hist_{symbol}_{period}_{interval}"
        if cache_key in stock_cache:
            return stock_cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return None
            
            # Convert to list of dictionaries
            data_points = []
            for date, row in hist.iterrows():
                data_points.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(float(row['Open']), 2),
                    "high": round(float(row['High']), 2),
                    "low": round(float(row['Low']), 2),
                    "close": round(float(row['Close']), 2),
                    "volume": int(row['Volume'])
                })
            
            # Get closing prices for ML
            closing_prices = [point['close'] for point in data_points]
            
            historical_data = {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "dataPoints": data_points,
                "closingPrices": closing_prices,
                "totalPoints": len(data_points),
                "startDate": data_points[0]["date"] if data_points else None,
                "endDate": data_points[-1]["date"] if data_points else None
            }
            
            stock_cache[cache_key] = historical_data
            return historical_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    @staticmethod
    def search_stocks(query: str) -> List[Dict[str, str]]:
        """
        Search for stocks by name or symbol
        
        Args:
            query: Search query
            
        Returns:
            List of matching stocks
        """
        query_lower = query.lower()
        
        # First, search in popular stocks
        matches = [
            stock for stock in StockService.POPULAR_STOCKS
            if query_lower in stock["symbol"].lower() 
            or query_lower in stock["name"].lower()
        ]
        
        # If we have matches, return them
        if matches:
            return matches[:10]
        
        # Otherwise, try to validate the symbol directly
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            if info.get("regularMarketPrice") or info.get("currentPrice"):
                return [{
                    "symbol": query.upper(),
                    "name": info.get("longName", info.get("shortName", query.upper()))
                }]
        except:
            pass
        
        return []
    
    @staticmethod
    def get_popular_stocks() -> List[Dict[str, str]]:
        """Get list of popular stocks"""
        return StockService.POPULAR_STOCKS
    
    @staticmethod
    def _format_market_cap(market_cap: int) -> str:
        """Format market cap to human readable string"""
        if market_cap >= 1e12:
            return f"${market_cap / 1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap / 1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap / 1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}"
