"""
Alpha Trend AI - FastAPI Backend
Deep Learning Stock Prediction API
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from .config import settings
from .routes import stocks_router, predictions_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Alpha Trend AI Backend...")
    logger.info("📊 LSTM Models ready for training")
    logger.info("📈 Yahoo Finance API connected")
    yield
    # Shutdown
    logger.info("🛑 Shutting down Alpha Trend AI Backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(stocks_router)
app.include_router(predictions_router)


# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - API health check and information
    """
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "message": "Welcome to Alpha Trend AI - Deep Learning Stock Prediction API",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "stocks": "/api/stocks",
            "predictions": "/api/predictions"
        },
        "features": [
            "Real-time stock data from Yahoo Finance",
            "LSTM-based price predictions",
            "Technical indicators (MA, RSI, MACD, Bollinger Bands)",
            "Model backtesting",
            "Prediction caching"
        ]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "api_version": settings.API_VERSION
    }


@app.get("/api", tags=["Health"])
async def api_info():
    """
    API information endpoint
    """
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": "Deep Learning Stock Prediction API using LSTM Neural Networks",
        "author": "RANGESHPANDIAN PT",
        "endpoints": {
            "stocks": {
                "list": "GET /api/stocks",
                "search": "GET /api/stocks/search?q=<query>",
                "details": "GET /api/stocks/{symbol}",
                "price": "GET /api/stocks/{symbol}/price",
                "history": "GET /api/stocks/{symbol}/history",
                "indicators": "GET /api/stocks/{symbol}/indicators",
                "signals": "GET /api/stocks/{symbol}/signals"
            },
            "predictions": {
                "predict": "GET /api/predictions/{symbol}",
                "quick": "GET /api/predictions/{symbol}/quick",
                "custom": "POST /api/predictions/custom",
                "backtest": "GET /api/predictions/{symbol}/backtest",
                "cache_info": "GET /api/predictions/cache/info",
                "clear_cache": "DELETE /api/predictions/cache"
            }
        },
        "model_info": {
            "type": "LSTM (Long Short-Term Memory)",
            "framework": "TensorFlow/Keras",
            "layers": 3,
            "default_lookback": settings.LOOKBACK_PERIOD,
            "default_epochs": settings.TRAINING_EPOCHS
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
