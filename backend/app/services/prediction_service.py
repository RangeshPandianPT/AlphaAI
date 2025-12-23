"""
Prediction Service - Manages LSTM model training and predictions
"""
from typing import Dict, List, Optional, Any
from ..models.lstm_model import LSTMPredictor
from ..config import settings
from .stock_service import StockService
import logging
from cachetools import TTLCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for trained models (1 hour TTL)
model_cache: Dict[str, LSTMPredictor] = {}
prediction_cache = TTLCache(maxsize=50, ttl=3600)


class PredictionService:
    """
    Service for managing stock price predictions using LSTM
    """
    
    @staticmethod
    def train_and_predict(
        symbol: str,
        lookback: int = 60,
        prediction_days: int = 7,
        epochs: int = 50,
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """
        Train LSTM model and generate predictions for a stock
        
        Args:
            symbol: Stock ticker symbol
            lookback: Look back period for LSTM
            prediction_days: Number of days to predict
            epochs: Training epochs
            force_retrain: Force model retraining even if cached
            
        Returns:
            Dictionary with training metrics and predictions
        """
        cache_key = f"pred_{symbol}_{lookback}_{prediction_days}"
        
        # Check prediction cache first (unless force retrain)
        if not force_retrain and cache_key in prediction_cache:
            logger.info(f"Returning cached predictions for {symbol}")
            return prediction_cache[cache_key]
        
        # Get historical data
        historical = StockService.get_historical_data(symbol, period="2y")
        
        if not historical or not historical.get("closingPrices"):
            raise ValueError(f"Could not fetch historical data for {symbol}")
        
        prices = historical["closingPrices"]
        
        if len(prices) < lookback + 20:
            raise ValueError(
                f"Not enough historical data for {symbol}. "
                f"Need at least {lookback + 20} days, got {len(prices)}"
            )
        
        # Check if we have a cached model (and not forcing retrain)
        if not force_retrain and symbol in model_cache:
            logger.info(f"Using cached model for {symbol}")
            predictor = model_cache[symbol]
        else:
            # Create and train new model
            logger.info(f"Training new LSTM model for {symbol}")
            predictor = LSTMPredictor(
                lookback=lookback,
                lstm_units=settings.LSTM_UNITS,
                dropout_rate=settings.LSTM_DROPOUT,
                epochs=epochs,
                batch_size=settings.BATCH_SIZE
            )
            
            training_metrics = predictor.train(prices)
            model_cache[symbol] = predictor
            
            logger.info(f"Model trained for {symbol}: {training_metrics}")
        
        # Generate predictions
        predictions = predictor.predict(prices, days_ahead=prediction_days)
        
        # Calculate price statistics
        current_price = prices[-1]
        predicted_end_price = predictions[-1]["predicted_price"]
        price_change = predicted_end_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        # Determine trend
        if price_change_pct > 2:
            trend = "bullish"
            trend_icon = "📈"
        elif price_change_pct < -2:
            trend = "bearish"
            trend_icon = "📉"
        else:
            trend = "neutral"
            trend_icon = "➡️"
        
        result = {
            "symbol": symbol,
            "currentPrice": round(current_price, 2),
            "predictions": predictions,
            "summary": {
                "predictedEndPrice": round(predicted_end_price, 2),
                "priceChange": round(price_change, 2),
                "priceChangePercent": round(price_change_pct, 2),
                "trend": trend,
                "trendIcon": trend_icon,
                "dataPointsUsed": len(prices),
                "lookbackPeriod": lookback,
                "predictionDays": prediction_days
            },
            "modelInfo": {
                "type": "LSTM",
                "layers": 3,
                "units": settings.LSTM_UNITS,
                "dropout": settings.LSTM_DROPOUT
            }
        }
        
        # Cache the result
        prediction_cache[cache_key] = result
        
        return result
    
    @staticmethod
    def get_quick_prediction(symbol: str) -> Dict[str, Any]:
        """
        Get a quick prediction using default settings
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Prediction results
        """
        return PredictionService.train_and_predict(
            symbol=symbol,
            lookback=settings.LOOKBACK_PERIOD,
            prediction_days=settings.PREDICTION_DAYS,
            epochs=settings.TRAINING_EPOCHS
        )
    
    @staticmethod
    def get_cached_model_info() -> Dict[str, Any]:
        """Get information about cached models"""
        return {
            "cachedModels": list(model_cache.keys()),
            "modelCount": len(model_cache),
            "predictionCacheSize": len(prediction_cache)
        }
    
    @staticmethod
    def clear_cache(symbol: Optional[str] = None) -> Dict[str, str]:
        """
        Clear model and prediction cache
        
        Args:
            symbol: Specific symbol to clear (None for all)
            
        Returns:
            Status message
        """
        global model_cache, prediction_cache
        
        if symbol:
            if symbol in model_cache:
                del model_cache[symbol]
            # Clear related predictions from cache
            keys_to_remove = [k for k in prediction_cache.keys() if symbol in k]
            for key in keys_to_remove:
                del prediction_cache[key]
            return {"status": f"Cleared cache for {symbol}"}
        else:
            model_cache = {}
            prediction_cache.clear()
            return {"status": "Cleared all caches"}
