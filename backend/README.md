# Alpha Trend AI - Backend

🚀 **Deep Learning Stock Prediction API** powered by LSTM Neural Networks

## 📋 Overview

This is the Python FastAPI backend for Alpha Trend AI. It provides:

- Real-time stock data from **Yahoo Finance**
- **LSTM-based** stock price predictions using TensorFlow
- Technical indicators (Moving Averages, RSI, MACD, Bollinger Bands)
- RESTful API endpoints for the frontend

## 🛠️ Setup

### Prerequisites

- Python 3.9+ 
- pip (Python package manager)

### Installation

1. **Create a virtual environment:**

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the server:**

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m uvicorn app.main:app --reload --port 8000
```

4. **Access the API:**

- API Root: http://localhost:8000
- Interactive Docs (Swagger): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

## 📚 API Endpoints

### Stocks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stocks` | List popular stocks |
| GET | `/api/stocks/search?q=<query>` | Search stocks |
| GET | `/api/stocks/{symbol}` | Get stock details |
| GET | `/api/stocks/{symbol}/price` | Get current price |
| GET | `/api/stocks/{symbol}/history` | Get historical data |
| GET | `/api/stocks/{symbol}/indicators` | Get technical indicators |
| GET | `/api/stocks/{symbol}/signals` | Get trading signals |

### Predictions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/predictions/{symbol}` | Get LSTM predictions |
| GET | `/api/predictions/{symbol}/quick` | Quick prediction (default params) |
| POST | `/api/predictions/custom` | Custom prediction with parameters |
| GET | `/api/predictions/{symbol}/backtest` | Backtest model accuracy |
| GET | `/api/predictions/cache/info` | View cached models |
| DELETE | `/api/predictions/cache` | Clear prediction cache |

## 🧠 LSTM Model

The prediction engine uses a **3-layer LSTM neural network**:

```
Input Layer (60 timesteps × 1 feature)
    ↓
LSTM Layer 1 (50 units, return sequences)
    ↓
Dropout (20%)
    ↓
LSTM Layer 2 (50 units, return sequences)
    ↓
Dropout (20%)
    ↓
LSTM Layer 3 (50 units)
    ↓
Dropout (20%)
    ↓
Dense Layer (25 units, ReLU)
    ↓
Output Layer (1 unit - predicted price)
```

### Model Parameters

- **Lookback Period:** 60 days (customizable)
- **Training Epochs:** 50 (with early stopping)
- **Batch Size:** 32
- **Optimizer:** Adam (lr=0.001)
- **Loss Function:** Mean Squared Error

## 📈 Technical Indicators

The API calculates these technical indicators:

- **SMA** (Simple Moving Average) - 10, 20, 50 periods
- **EMA** (Exponential Moving Average) - 12, 26 periods
- **RSI** (Relative Strength Index) - 14 period
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands** - 20 period, 2 standard deviations

## 🔧 Configuration

Edit `app/config.py` to customize:

```python
class Settings:
    # LSTM Settings
    LSTM_UNITS = 50
    LSTM_DROPOUT = 0.2
    LOOKBACK_PERIOD = 60
    PREDICTION_DAYS = 7
    TRAINING_EPOCHS = 50
    
    # Cache TTL (seconds)
    CACHE_TTL = 300
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Configuration
│   ├── models/
│   │   └── lstm_model.py    # LSTM architecture
│   ├── services/
│   │   ├── stock_service.py # Yahoo Finance integration
│   │   └── prediction_service.py
│   ├── routes/
│   │   ├── stocks.py        # Stock endpoints
│   │   └── predictions.py   # Prediction endpoints
│   └── utils/
│       └── indicators.py    # Technical indicators
├── requirements.txt
└── README.md
```

## 🚀 Example Usage

### Get Stock Price

```bash
curl http://localhost:8000/api/stocks/AAPL/price
```

### Get LSTM Predictions

```bash
curl http://localhost:8000/api/predictions/AAPL?days=7
```

### Custom Prediction

```bash
curl -X POST http://localhost:8000/api/predictions/custom \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "TSLA",
    "lookback": 60,
    "prediction_days": 14,
    "epochs": 100
  }'
```

## 🔮 Future Enhancements

- [ ] Add sentiment analysis from news
- [ ] Multi-stock portfolio predictions
- [ ] Real-time WebSocket updates
- [ ] Model persistence (save/load trained models)
- [ ] GPU acceleration for faster training

## ✍️ Author

Developed with ❤️ by **RANGESHPANDIAN PT**
