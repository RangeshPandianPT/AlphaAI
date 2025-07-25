import { useState } from "react";
import { Search, TrendingUp } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface StockSearchProps {
  onSymbolSelect: (symbol: string) => void;
  currentSymbol?: string;
}

const popularStocks = [
  { symbol: "AAPL", name: "Apple Inc." },
  { symbol: "MSFT", name: "Microsoft Corporation" },
  { symbol: "GOOGL", name: "Alphabet Inc." },
  { symbol: "AMZN", name: "Amazon.com Inc." },
  { symbol: "TSLA", name: "Tesla Inc." },
  { symbol: "NVDA", name: "NVIDIA Corporation" }
];

export function StockSearch({ onSymbolSelect, currentSymbol }: StockSearchProps) {
  const [searchValue, setSearchValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchValue.trim()) {
      onSymbolSelect(searchValue.trim().toUpperCase());
      setSearchValue("");
    }
  };

  return (
    <Card className="bg-gradient-card border-border/50 backdrop-blur-sm p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold">Stock Search</h2>
        </div>
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="Enter stock symbol (e.g., AAPL)"
              className="pl-10 bg-background/50 border-border/50 focus:bg-background"
            />
          </div>
          <Button type="submit" variant="trading">
            Search
          </Button>
        </form>
        
        <div>
          <p className="text-sm text-muted-foreground mb-3">Popular Stocks:</p>
          <div className="grid grid-cols-2 gap-2">
            {popularStocks.map((stock) => (
              <Button
                key={stock.symbol}
                variant={currentSymbol === stock.symbol ? "default" : "outline"}
                size="sm"
                onClick={() => onSymbolSelect(stock.symbol)}
                className="justify-start text-left h-auto py-2"
              >
                <div>
                  <div className="font-medium">{stock.symbol}</div>
                  <div className="text-xs text-muted-foreground truncate">
                    {stock.name}
                  </div>
                </div>
              </Button>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}