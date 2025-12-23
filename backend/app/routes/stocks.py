"""
Stock Data API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.stock_service import StockService
from ..utils.indicators import TechnicalIndicators

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])


@router.get("/")
async def get_popular_stocks():
    """
    Get a list of popular stocks
    """
    return {
        "stocks": StockService.get_popular_stocks(),
        "count": len(StockService.POPULAR_STOCKS)
    }


@router.get("/search")
async def search_stocks(
    q: str = Query(..., min_length=1, description="Search query")
):
    """
    Search for stocks by name or symbol
    """
    results = StockService.search_stocks(q)
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }


@router.get("/{symbol}")
async def get_stock_data(symbol: str):
    """
    Get current stock data including price and basic info
    """
    symbol = symbol.upper()
    
    # Get stock info
    info = StockService.get_stock_info(symbol)
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found"
        )
    
    # Get current price
    price_data = StockService.get_current_price(symbol)
    if not price_data:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch price data for {symbol}"
        )
    
    return {
        "info": info,
        "price": price_data
    }


@router.get("/{symbol}/price")
async def get_stock_price(symbol: str):
    """
    Get current stock price with change information
    """
    symbol = symbol.upper()
    price_data = StockService.get_current_price(symbol)
    
    if not price_data:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch price for {symbol}"
        )
    
    return price_data


@router.get("/{symbol}/history")
async def get_stock_history(
    symbol: str,
    period: str = Query(
        default="1y",
        description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max"
    ),
    interval: str = Query(
        default="1d",
        description="Data interval: 1d, 1wk, 1mo"
    )
):
    """
    Get historical stock data
    """
    symbol = symbol.upper()
    
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
    valid_intervals = ["1d", "1wk", "1mo"]
    
    if period not in valid_periods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period. Must be one of: {valid_periods}"
        )
    
    if interval not in valid_intervals:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval. Must be one of: {valid_intervals}"
        )
    
    historical = StockService.get_historical_data(symbol, period, interval)
    
    if not historical:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch historical data for {symbol}"
        )
    
    return historical


@router.get("/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    period: str = Query(default="1y", description="Historical data period")
):
    """
    Get all technical indicators for a stock
    """
    symbol = symbol.upper()
    
    # Get historical data
    historical = StockService.get_historical_data(symbol, period)
    
    if not historical or not historical.get("closingPrices"):
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch data for {symbol}"
        )
    
    prices = historical["closingPrices"]
    
    # Calculate indicators
    indicators = TechnicalIndicators.calculate_all_indicators(prices)
    
    # Get current signals
    signals = TechnicalIndicators.get_current_signals(prices)
    
    return {
        "symbol": symbol,
        "period": period,
        "dataPoints": len(prices),
        "indicators": indicators,
        "signals": signals
    }


@router.get("/{symbol}/signals")
async def get_trading_signals(symbol: str):
    """
    Get current trading signals based on technical analysis
    """
    symbol = symbol.upper()
    
    # Get historical data
    historical = StockService.get_historical_data(symbol, "6mo")
    
    if not historical or not historical.get("closingPrices"):
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch data for {symbol}"
        )
    
    prices = historical["closingPrices"]
    signals = TechnicalIndicators.get_current_signals(prices)
    
    return {
        "symbol": symbol,
        **signals
    }
