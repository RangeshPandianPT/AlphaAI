"""
LSTM Neural Network Model for Stock Price Prediction
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LSTMPredictor:
    """
    LSTM-based stock price predictor using TensorFlow/Keras
    """
    
    def __init__(
        self,
        lookback: int = 60,
        lstm_units: int = 50,
        dropout_rate: float = 0.2,
        epochs: int = 50,
        batch_size: int = 32
    ):
        """
        Initialize the LSTM Predictor
        
        Args:
            lookback: Number of days to look back for prediction
            lstm_units: Number of LSTM units per layer
            dropout_rate: Dropout rate for regularization
            epochs: Number of training epochs
            batch_size: Training batch size
        """
        self.lookback = lookback
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.model: Optional[Sequential] = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_trained = False
        
    def _build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """
        Build the LSTM model architecture
        
        Args:
            input_shape: Shape of input data (lookback, features)
            
        Returns:
            Compiled Keras Sequential model
        """
        model = Sequential([
            # First LSTM layer with return sequences
            LSTM(
                units=self.lstm_units,
                return_sequences=True,
                input_shape=input_shape
            ),
            Dropout(self.dropout_rate),
            
            # Second LSTM layer
            LSTM(
                units=self.lstm_units,
                return_sequences=True
            ),
            Dropout(self.dropout_rate),
            
            # Third LSTM layer
            LSTM(
                units=self.lstm_units,
                return_sequences=False
            ),
            Dropout(self.dropout_rate),
            
            # Dense layers for output
            Dense(units=25, activation='relu'),
            Dense(units=1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        return model
    
    def _create_sequences(
        self,
        data: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training
        
        Args:
            data: Normalized price data
            
        Returns:
            Tuple of (X, y) arrays for training
        """
        X, y = [], []
        
        for i in range(self.lookback, len(data)):
            X.append(data[i - self.lookback:i, 0])
            y.append(data[i, 0])
            
        return np.array(X), np.array(y)
    
    def train(
        self,
        prices: List[float],
        validation_split: float = 0.2
    ) -> dict:
        """
        Train the LSTM model on historical price data
        
        Args:
            prices: List of historical closing prices
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training history metrics
        """
        logger.info(f"Training LSTM model with {len(prices)} data points")
        
        # Convert to numpy array and reshape
        data = np.array(prices).reshape(-1, 1)
        
        # Normalize the data
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = self._create_sequences(scaled_data)
        
        if len(X) == 0:
            raise ValueError(
                f"Not enough data points. Need at least {self.lookback + 1} "
                f"data points, got {len(prices)}"
            )
        
        # Reshape X for LSTM [samples, time steps, features]
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        # Build the model
        self.model = self._build_model(input_shape=(X.shape[1], 1))
        
        # Early stopping callback
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train the model
        history = self.model.fit(
            X, y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=validation_split,
            callbacks=[early_stopping],
            verbose=1
        )
        
        self.is_trained = True
        
        # Return training metrics
        return {
            "final_loss": float(history.history['loss'][-1]),
            "final_mae": float(history.history['mae'][-1]),
            "final_val_loss": float(history.history['val_loss'][-1]),
            "final_val_mae": float(history.history['val_mae'][-1]),
            "epochs_trained": len(history.history['loss'])
        }
    
    def predict(
        self,
        prices: List[float],
        days_ahead: int = 7
    ) -> List[dict]:
        """
        Generate predictions for future days
        
        Args:
            prices: Recent historical prices (at least lookback days)
            days_ahead: Number of days to predict ahead
            
        Returns:
            List of prediction dictionaries with date and predicted price
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model must be trained before making predictions")
        
        if len(prices) < self.lookback:
            raise ValueError(
                f"Need at least {self.lookback} data points for prediction, "
                f"got {len(prices)}"
            )
        
        # Get the last 'lookback' days of data
        last_data = np.array(prices[-self.lookback:]).reshape(-1, 1)
        scaled_data = self.scaler.transform(last_data)
        
        predictions = []
        current_sequence = scaled_data.flatten().tolist()
        
        for day in range(days_ahead):
            # Prepare input
            X = np.array(current_sequence[-self.lookback:]).reshape(1, self.lookback, 1)
            
            # Make prediction
            pred_scaled = self.model.predict(X, verbose=0)[0, 0]
            
            # Inverse transform to get actual price
            pred_price = self.scaler.inverse_transform([[pred_scaled]])[0, 0]
            
            # Calculate prediction date
            from datetime import datetime, timedelta
            pred_date = datetime.now() + timedelta(days=day + 1)
            
            predictions.append({
                "date": pred_date.strftime("%Y-%m-%d"),
                "day": day + 1,
                "predicted_price": round(float(pred_price), 2),
                "confidence": self._calculate_confidence(day)
            })
            
            # Update sequence for next prediction
            current_sequence.append(pred_scaled)
        
        return predictions
    
    def _calculate_confidence(self, day: int) -> float:
        """
        Calculate prediction confidence (decreases with time)
        
        Args:
            day: Day number (0-indexed)
            
        Returns:
            Confidence score (0-100)
        """
        # Confidence decreases exponentially with prediction horizon
        base_confidence = 90
        decay_rate = 0.05
        confidence = base_confidence * np.exp(-decay_rate * day)
        return round(float(confidence), 1)
    
    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        if self.model is None:
            return "Model not built yet"
        
        summary_list = []
        self.model.summary(print_fn=lambda x: summary_list.append(x))
        return "\n".join(summary_list)
