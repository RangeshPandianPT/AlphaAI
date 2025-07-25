// Mock stock data service - in production, replace with real API
export interface StockData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: string;
  historicalData: HistoricalPoint[];
}

export interface HistoricalPoint {
  date: string;
  price: number;
  volume: number;
}

class StockService {
  private generateMockData(symbol: string, days: number = 30): HistoricalPoint[] {
    const data: HistoricalPoint[] = [];
    const basePrice = this.getBasePrice(symbol);
    let currentPrice = basePrice;
    
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      // Add some realistic price movement
      const volatility = 0.02;
      const randomChange = (Math.random() - 0.5) * volatility;
      currentPrice = currentPrice * (1 + randomChange);
      
      data.push({
        date: date.toISOString().split('T')[0],
        price: parseFloat(currentPrice.toFixed(2)),
        volume: Math.floor(Math.random() * 10000000) + 1000000
      });
    }
    
    return data;
  }

  private getBasePrice(symbol: string): number {
    const basePrices: Record<string, number> = {
      'AAPL': 175,
      'MSFT': 380,
      'GOOGL': 140,
      'AMZN': 145,
      'TSLA': 240,
      'NVDA': 480,
    };
    return basePrices[symbol] || 100;
  }

  private calculateMarketCap(symbol: string, price: number): string {
    const shares: Record<string, number> = {
      'AAPL': 15.5e9,
      'MSFT': 7.4e9,
      'GOOGL': 12.6e9,
      'AMZN': 10.5e9,
      'TSLA': 3.2e9,
      'NVDA': 24.6e9,
    };
    
    const shareCount = shares[symbol] || 1e9;
    const marketCap = price * shareCount;
    
    if (marketCap >= 1e12) {
      return `$${(marketCap / 1e12).toFixed(1)}T`;
    } else if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(1)}B`;
    } else {
      return `$${(marketCap / 1e6).toFixed(1)}M`;
    }
  }

  async getStockData(symbol: string): Promise<StockData> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const historicalData = this.generateMockData(symbol);
    const currentPrice = historicalData[historicalData.length - 1].price;
    const previousPrice = historicalData[historicalData.length - 2].price;
    const change = currentPrice - previousPrice;
    const changePercent = (change / previousPrice) * 100;
    
    return {
      symbol,
      price: currentPrice,
      change,
      changePercent,
      volume: historicalData[historicalData.length - 1].volume,
      marketCap: this.calculateMarketCap(symbol, currentPrice),
      historicalData
    };
  }

  // Technical indicators
  calculateMovingAverage(data: HistoricalPoint[], period: number): number[] {
    const ma: number[] = [];
    
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        ma.push(NaN);
      } else {
        const sum = data.slice(i - period + 1, i + 1).reduce((acc, point) => acc + point.price, 0);
        ma.push(sum / period);
      }
    }
    
    return ma;
  }

  calculateRSI(data: HistoricalPoint[], period: number = 14): number[] {
    const rsi: number[] = [];
    const gains: number[] = [];
    const losses: number[] = [];
    
    for (let i = 1; i < data.length; i++) {
      const change = data[i].price - data[i - 1].price;
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? Math.abs(change) : 0);
    }
    
    for (let i = 0; i < gains.length; i++) {
      if (i < period - 1) {
        rsi.push(NaN);
      } else {
        const avgGain = gains.slice(i - period + 1, i + 1).reduce((a, b) => a + b) / period;
        const avgLoss = losses.slice(i - period + 1, i + 1).reduce((a, b) => a + b) / period;
        
        if (avgLoss === 0) {
          rsi.push(100);
        } else {
          const rs = avgGain / avgLoss;
          rsi.push(100 - (100 / (1 + rs)));
        }
      }
    }
    
    return [NaN, ...rsi]; // Add NaN for the first data point since we start from index 1
  }
}

export const stockService = new StockService();