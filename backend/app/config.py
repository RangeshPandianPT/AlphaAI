"""
Configuration settings for Alpha Trend AI Backend
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # API Settings
    API_TITLE = "Alpha Trend AI API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = """
    🚀 Alpha Trend AI - Deep Learning Stock Prediction API
    
    This API provides:
    - Real-time stock data from Yahoo Finance
    - LSTM-based stock price predictions
    - Technical indicators (Moving Averages, RSI)
    - Historical data analysis
    """
    
    # CORS Settings
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "*"  # Allow all origins in development
    ]
    
    # Model Settings
    LSTM_UNITS = 50
    LSTM_DROPOUT = 0.2
    LOOKBACK_PERIOD = 60  # Days of historical data for prediction
    PREDICTION_DAYS = 7   # Days to predict ahead
    TRAINING_EPOCHS = 50
    BATCH_SIZE = 32
    
    # Cache Settings
    CACHE_TTL = 300  # 5 minutes cache for stock data
    
    # Data Settings
    DEFAULT_HISTORY_PERIOD = "1y"  # 1 year of historical data
    
settings = Settings()
