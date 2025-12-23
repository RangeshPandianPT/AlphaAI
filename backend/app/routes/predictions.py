"""
Prediction API Routes
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
from ..services.prediction_service import PredictionService

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


class PredictionRequest(BaseModel):
    """Request model for custom predictions"""
    symbol: str = Field(..., description="Stock ticker symbol")
    lookback: int = Field(default=60, ge=20, le=120, description="Lookback period")
    prediction_days: int = Field(default=7, ge=1, le=30, description="Days to predict")
    epochs: int = Field(default=50, ge=10, le=200, description="Training epochs")
    force_retrain: bool = Field(default=False, description="Force model retraining")


@router.get("/{symbol}")
async def get_prediction(
    symbol: str,
    days: int = Query(default=7, ge=1, le=30, description="Days to predict ahead")
):
    """
    Get AI-powered stock price predictions using LSTM
    
    This endpoint trains an LSTM model on historical data and generates
    predictions for the specified number of days ahead.
    """
    symbol = symbol.upper()
    
    try:
        result = PredictionService.train_and_predict(
            symbol=symbol,
            prediction_days=days
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/custom")
async def create_custom_prediction(request: PredictionRequest):
    """
    Create a custom prediction with specified parameters
    
    Allows fine-tuning of:
    - Lookback period (how much historical data to use)
    - Prediction horizon (days ahead)
    - Training epochs
    - Force retraining of cached model
    """
    try:
        result = PredictionService.train_and_predict(
            symbol=request.symbol.upper(),
            lookback=request.lookback,
            prediction_days=request.prediction_days,
            epochs=request.epochs,
            force_retrain=request.force_retrain
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/{symbol}/quick")
async def get_quick_prediction(symbol: str):
    """
    Get a quick prediction using default settings
    
    Uses optimal default parameters for fast predictions.
    Results are cached for 1 hour.
    """
    symbol = symbol.upper()
    
    try:
        result = PredictionService.get_quick_prediction(symbol)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/cache/info")
async def get_cache_info():
    """
    Get information about cached models and predictions
    """
    return PredictionService.get_cached_model_info()


@router.delete("/cache")
async def clear_cache(
    symbol: Optional[str] = Query(
        default=None,
        description="Specific symbol to clear (omit for all)"
    )
):
    """
    Clear prediction cache
    
    Optionally specify a symbol to clear only that stock's cache,
    or leave empty to clear all caches.
    """
    return PredictionService.clear_cache(symbol)


@router.get("/{symbol}/backtest")
async def backtest_model(
    symbol: str,
    test_days: int = Query(default=30, ge=7, le=90, description="Days to use for testing")
):
    """
    Backtest the LSTM model on historical data
    
    Splits data into training and test sets, trains the model,
    and evaluates prediction accuracy on the test set.
    """
    from ..services.stock_service import StockService
    from ..models.lstm_model import LSTMPredictor
    import numpy as np
    
    symbol = symbol.upper()
    
    try:
        # Get historical data
        historical = StockService.get_historical_data(symbol, period="2y")
        
        if not historical or not historical.get("closingPrices"):
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch data for {symbol}"
            )
        
        prices = historical["closingPrices"]
        
        if len(prices) < 120 + test_days:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough data for backtesting. Need at least {120 + test_days} days."
            )
        
        # Split data
        train_prices = prices[:-test_days]
        test_prices = prices[-test_days:]
        
        # Train model
        predictor = LSTMPredictor(lookback=60, epochs=30)
        training_metrics = predictor.train(train_prices)
        
        # Make predictions for test period
        predictions = []
        for i in range(len(test_prices)):
            input_prices = prices[:-(test_days - i)] if i > 0 else train_prices
            pred = predictor.predict(input_prices, days_ahead=1)
            predictions.append(pred[0]["predicted_price"])
        
        # Calculate accuracy metrics
        actual = np.array(test_prices)
        predicted = np.array(predictions)
        
        mae = np.mean(np.abs(actual - predicted))
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # Direction accuracy
        actual_direction = np.diff(actual) > 0
        predicted_direction = np.diff(predicted) > 0
        direction_accuracy = np.mean(actual_direction == predicted_direction) * 100
        
        return {
            "symbol": symbol,
            "testDays": test_days,
            "trainingMetrics": training_metrics,
            "backtestResults": {
                "mae": round(float(mae), 2),
                "mape": round(float(mape), 2),
                "rmse": round(float(rmse), 2),
                "directionAccuracy": round(float(direction_accuracy), 2)
            },
            "comparison": [
                {
                    "day": i + 1,
                    "actual": round(float(test_prices[i]), 2),
                    "predicted": round(float(predictions[i]), 2),
                    "error": round(float(abs(test_prices[i] - predictions[i])), 2)
                }
                for i in range(min(10, len(test_prices)))  # Show first 10 days
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest failed: {str(e)}"
        )
