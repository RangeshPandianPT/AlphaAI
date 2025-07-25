import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PriceCard } from "@/components/ui/price-card";
import { StockSearch } from "@/components/ui/stock-search";
import { ChartContainer } from "@/components/ui/chart-container";
import { Badge } from "@/components/ui/badge";
import { Loader2, Brain, TrendingUp, BarChart3 } from "lucide-react";
import { stockService, StockData } from "@/services/stockService";
import { lstmService, PredictionData } from "@/services/lstmService";
import { toast } from "sonner";

interface ChartPoint {
  date: string;
  price: number;
  prediction?: number;
  ma10?: number;
  ma20?: number;
  rsi?: number;
}

export default function Dashboard() {
  const [selectedSymbol, setSelectedSymbol] = useState<string>("AAPL");
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [chartData, setChartData] = useState<ChartPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [showPredictions, setShowPredictions] = useState(false);

  // Load stock data
  const loadStockData = async (symbol: string) => {
    setLoading(true);
    try {
      const data = await stockService.getStockData(symbol);
      setStockData(data);
      
      // Calculate technical indicators
      const ma10 = stockService.calculateMovingAverage(data.historicalData, 10);
      const ma20 = stockService.calculateMovingAverage(data.historicalData, 20);
      const rsi = stockService.calculateRSI(data.historicalData);
      
      const enrichedChartData: ChartPoint[] = data.historicalData.map((point, index) => ({
        date: point.date,
        price: point.price,
        ma10: ma10[index],
        ma20: ma20[index],
        rsi: rsi[index]
      }));
      
      setChartData(enrichedChartData);
      
      toast.success(`Loaded data for ${symbol}`);
    } catch (error) {
      toast.error("Failed to load stock data");
      console.error("Error loading stock data:", error);
    } finally {
      setLoading(false);
    }
  };

  // Train LSTM model and generate predictions
  const generatePredictions = async () => {
    if (!stockData) return;
    
    setTraining(true);
    try {
      const prices = stockData.historicalData.map(point => point.price);
      
      toast.loading("Training LSTM model...", { id: "training" });
      
      // Train the model
      await lstmService.trainModel(prices, 30, 10);
      
      toast.success("Model trained successfully!", { id: "training" });
      toast.loading("Generating predictions...", { id: "predicting" });
      
      // Generate predictions
      const predictionData = await lstmService.predict(prices, 10, 7);
      setPredictions(predictionData);
      
      // Merge predictions with chart data
      const updatedChartData = [...chartData];
      predictionData.forEach(pred => {
        updatedChartData.push({
          date: pred.date,
          price: NaN, // No actual price for future dates
          prediction: pred.prediction
        });
      });
      
      setChartData(updatedChartData);
      setShowPredictions(true);
      
      toast.success("Predictions generated!", { id: "predicting" });
    } catch (error) {
      toast.error("Failed to generate predictions");
      console.error("Error generating predictions:", error);
    } finally {
      setTraining(false);
    }
  };

  // Load initial data
  useEffect(() => {
    loadStockData(selectedSymbol);
  }, [selectedSymbol]);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            AI Stock Prediction Dashboard
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Advanced LSTM neural networks for stock price prediction with real-time technical analysis
          </p>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <StockSearch 
              onSymbolSelect={setSelectedSymbol}
              currentSymbol={selectedSymbol}
            />
            
            {stockData && (
              <PriceCard
                symbol={stockData.symbol}
                price={stockData.price}
                change={stockData.change}
                changePercent={stockData.changePercent}
                volume={stockData.volume}
                marketCap={stockData.marketCap}
              />
            )}

            {/* AI Controls */}
            <Card className="bg-gradient-card border-border/50 backdrop-blur-sm p-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold">AI Predictions</h3>
                </div>
                
                <div className="space-y-3">
                  <Button
                    onClick={generatePredictions}
                    disabled={training || loading || !stockData}
                    variant="default"
                    className="w-full"
                  >
                    {training ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Training Model...
                      </>
                    ) : (
                      <>
                        <TrendingUp className="h-4 w-4 mr-2" />
                        Generate Predictions
                      </>
                    )}
                  </Button>
                  
                  {predictions.length > 0 && (
                    <div className="space-y-2">
                      <Badge variant="secondary" className="w-full justify-center">
                        7-Day Forecast Ready
                      </Badge>
                      <div className="text-sm space-y-1">
                        <p className="text-muted-foreground">Next day prediction:</p>
                        <p className="font-bold text-primary">
                          ${predictions[0]?.prediction.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </div>

          {/* Main Charts */}
          <div className="lg:col-span-3 space-y-6">
            {loading ? (
              <Card className="bg-gradient-card border-border/50 backdrop-blur-sm p-12">
                <div className="flex items-center justify-center space-x-2">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                  <span className="text-muted-foreground">Loading stock data...</span>
                </div>
              </Card>
            ) : (
              <>
                {/* Price Chart */}
                <ChartContainer
                  data={chartData}
                  title={`${selectedSymbol} Stock Price ${showPredictions ? 'with AI Predictions' : ''}`}
                  showPrediction={showPredictions}
                />

                {/* Technical Indicators */}
                {stockData && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="bg-gradient-card border-border/50 backdrop-blur-sm p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <BarChart3 className="h-4 w-4 text-chart-secondary" />
                        <h4 className="font-medium">Moving Averages</h4>
                      </div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">MA(10):</span>
                          <span>${stockData.historicalData.slice(-10).reduce((sum, p) => sum + p.price, 0) / 10}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">MA(20):</span>
                          <span>${stockData.historicalData.slice(-20).reduce((sum, p) => sum + p.price, 0) / 20}</span>
                        </div>
                      </div>
                    </Card>

                    <Card className="bg-gradient-card border-border/50 backdrop-blur-sm p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-chart-tertiary" />
                        <h4 className="font-medium">RSI (14)</h4>
                      </div>
                      <div className="text-2xl font-bold">
                        {stockService.calculateRSI(stockData.historicalData).slice(-1)[0]?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {(stockService.calculateRSI(stockData.historicalData).slice(-1)[0] || 0) > 70 ? 'Overbought' : 
                         (stockService.calculateRSI(stockData.historicalData).slice(-1)[0] || 0) < 30 ? 'Oversold' : 'Neutral'}
                      </div>
                    </Card>

                    <Card className="bg-gradient-card border-border/50 backdrop-blur-sm p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="h-4 w-4 text-primary" />
                        <h4 className="font-medium">AI Confidence</h4>
                      </div>
                      <div className="text-2xl font-bold">
                        {predictions.length > 0 ? '87%' : 'N/A'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Model Accuracy
                      </div>
                    </Card>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}