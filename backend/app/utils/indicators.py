"""
Technical Indicators Utility
Calculate various technical analysis indicators
"""
import numpy as np
from typing import List, Dict, Any, Optional


class TechnicalIndicators:
    """
    Calculate technical analysis indicators for stock data
    """
    
    @staticmethod
    def moving_average(
        prices: List[float],
        period: int
    ) -> List[Optional[float]]:
        """
        Calculate Simple Moving Average (SMA)
        
        Args:
            prices: List of closing prices
            period: MA period (e.g., 10, 20, 50, 200)
            
        Returns:
            List of MA values (None for initial period)
        """
        if len(prices) < period:
            return [None] * len(prices)
        
        ma = []
        for i in range(len(prices)):
            if i < period - 1:
                ma.append(None)
            else:
                avg = sum(prices[i - period + 1:i + 1]) / period
                ma.append(round(avg, 2))
        
        return ma
    
    @staticmethod
    def exponential_moving_average(
        prices: List[float],
        period: int
    ) -> List[Optional[float]]:
        """
        Calculate Exponential Moving Average (EMA)
        
        Args:
            prices: List of closing prices
            period: EMA period
            
        Returns:
            List of EMA values
        """
        if len(prices) < period:
            return [None] * len(prices)
        
        multiplier = 2 / (period + 1)
        ema = [None] * (period - 1)
        
        # First EMA is the SMA
        first_ema = sum(prices[:period]) / period
        ema.append(round(first_ema, 2))
        
        # Calculate subsequent EMAs
        for i in range(period, len(prices)):
            current_ema = (prices[i] - ema[-1]) * multiplier + ema[-1]
            ema.append(round(current_ema, 2))
        
        return ema
    
    @staticmethod
    def rsi(
        prices: List[float],
        period: int = 14
    ) -> List[Optional[float]]:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: List of closing prices
            period: RSI period (default 14)
            
        Returns:
            List of RSI values (0-100)
        """
        if len(prices) < period + 1:
            return [None] * len(prices)
        
        # Calculate price changes
        changes = []
        for i in range(1, len(prices)):
            changes.append(prices[i] - prices[i - 1])
        
        # Separate gains and losses
        gains = [max(0, change) for change in changes]
        losses = [max(0, -change) for change in changes]
        
        rsi_values = [None] * period
        
        # Calculate first average gain/loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Calculate RSI
        for i in range(period, len(changes)):
            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(round(rsi, 2))
            
            # Update averages (Wilder's smoothing)
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        # Add final RSI
        if avg_loss == 0:
            rsi_values.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(round(rsi, 2))
        
        return rsi_values
    
    @staticmethod
    def macd(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, List[Optional[float]]]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: List of closing prices
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)
            
        Returns:
            Dictionary with MACD line, signal line, and histogram
        """
        fast_ema = TechnicalIndicators.exponential_moving_average(prices, fast_period)
        slow_ema = TechnicalIndicators.exponential_moving_average(prices, slow_period)
        
        # MACD line = Fast EMA - Slow EMA
        macd_line = []
        for i in range(len(prices)):
            if fast_ema[i] is None or slow_ema[i] is None:
                macd_line.append(None)
            else:
                macd_line.append(round(fast_ema[i] - slow_ema[i], 2))
        
        # Signal line = EMA of MACD line
        valid_macd = [m for m in macd_line if m is not None]
        if len(valid_macd) < signal_period:
            signal_line = [None] * len(prices)
        else:
            signal_ema = TechnicalIndicators.exponential_moving_average(
                valid_macd, signal_period
            )
            # Pad with None to match original length
            signal_line = [None] * (len(prices) - len(signal_ema)) + signal_ema
        
        # Histogram = MACD - Signal
        histogram = []
        for i in range(len(prices)):
            if macd_line[i] is None or signal_line[i] is None:
                histogram.append(None)
            else:
                histogram.append(round(macd_line[i] - signal_line[i], 2))
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    @staticmethod
    def bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, List[Optional[float]]]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: List of closing prices
            period: MA period (default 20)
            std_dev: Standard deviation multiplier (default 2)
            
        Returns:
            Dictionary with upper, middle, and lower bands
        """
        ma = TechnicalIndicators.moving_average(prices, period)
        
        upper_band = []
        lower_band = []
        
        for i in range(len(prices)):
            if i < period - 1:
                upper_band.append(None)
                lower_band.append(None)
            else:
                # Calculate standard deviation
                window = prices[i - period + 1:i + 1]
                std = np.std(window)
                
                upper_band.append(round(ma[i] + std_dev * std, 2))
                lower_band.append(round(ma[i] - std_dev * std, 2))
        
        return {
            "upper": upper_band,
            "middle": ma,
            "lower": lower_band
        }
    
    @staticmethod
    def calculate_all_indicators(
        prices: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate all technical indicators for given prices
        
        Args:
            prices: List of closing prices
            
        Returns:
            Dictionary with all indicators
        """
        return {
            "sma10": TechnicalIndicators.moving_average(prices, 10),
            "sma20": TechnicalIndicators.moving_average(prices, 20),
            "sma50": TechnicalIndicators.moving_average(prices, 50),
            "ema12": TechnicalIndicators.exponential_moving_average(prices, 12),
            "ema26": TechnicalIndicators.exponential_moving_average(prices, 26),
            "rsi14": TechnicalIndicators.rsi(prices, 14),
            "macd": TechnicalIndicators.macd(prices),
            "bollingerBands": TechnicalIndicators.bollinger_bands(prices)
        }
    
    @staticmethod
    def get_current_signals(prices: List[float]) -> Dict[str, Any]:
        """
        Get current trading signals based on indicators
        
        Args:
            prices: List of closing prices
            
        Returns:
            Dictionary with trading signals
        """
        indicators = TechnicalIndicators.calculate_all_indicators(prices)
        
        current_price = prices[-1]
        signals = []
        
        # RSI signals
        current_rsi = indicators["rsi14"][-1]
        if current_rsi is not None:
            if current_rsi > 70:
                signals.append({
                    "indicator": "RSI",
                    "signal": "OVERBOUGHT",
                    "value": current_rsi,
                    "suggestion": "Consider selling"
                })
            elif current_rsi < 30:
                signals.append({
                    "indicator": "RSI",
                    "signal": "OVERSOLD",
                    "value": current_rsi,
                    "suggestion": "Consider buying"
                })
            else:
                signals.append({
                    "indicator": "RSI",
                    "signal": "NEUTRAL",
                    "value": current_rsi,
                    "suggestion": "Hold position"
                })
        
        # Moving Average signals
        sma20 = indicators["sma20"][-1]
        sma50 = indicators["sma50"][-1]
        
        if sma20 is not None and sma50 is not None:
            if sma20 > sma50:
                signals.append({
                    "indicator": "MA Crossover",
                    "signal": "BULLISH",
                    "value": f"SMA20 ({sma20}) > SMA50 ({sma50})",
                    "suggestion": "Uptrend detected"
                })
            else:
                signals.append({
                    "indicator": "MA Crossover",
                    "signal": "BEARISH",
                    "value": f"SMA20 ({sma20}) < SMA50 ({sma50})",
                    "suggestion": "Downtrend detected"
                })
        
        # Bollinger Bands signals
        bb = indicators["bollingerBands"]
        if bb["upper"][-1] is not None:
            if current_price > bb["upper"][-1]:
                signals.append({
                    "indicator": "Bollinger Bands",
                    "signal": "OVERBOUGHT",
                    "value": f"Price above upper band ({bb['upper'][-1]})",
                    "suggestion": "Potential reversal"
                })
            elif current_price < bb["lower"][-1]:
                signals.append({
                    "indicator": "Bollinger Bands",
                    "signal": "OVERSOLD",
                    "value": f"Price below lower band ({bb['lower'][-1]})",
                    "suggestion": "Potential reversal"
                })
        
        return {
            "currentPrice": current_price,
            "signals": signals,
            "indicators": {
                "rsi": current_rsi,
                "sma20": sma20,
                "sma50": sma50,
                "bollingerUpper": bb["upper"][-1],
                "bollingerLower": bb["lower"][-1]
            }
        }
