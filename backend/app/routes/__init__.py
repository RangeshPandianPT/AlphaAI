# Routes module
from .stocks import router as stocks_router
from .predictions import router as predictions_router

__all__ = ["stocks_router", "predictions_router"]
