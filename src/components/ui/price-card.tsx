import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface PriceCardProps {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  marketCap?: string;
  className?: string;
}

export function PriceCard({
  symbol,
  price,
  change,
  changePercent,
  volume,
  marketCap,
  className
}: PriceCardProps) {
  const isPositive = change >= 0;
  
  return (
    <Card className={cn(
      "bg-gradient-card border-border/50 backdrop-blur-sm p-6 hover:shadow-soft transition-all duration-300",
      className
    )}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-2xl font-bold text-foreground">{symbol}</h3>
          <div className={cn(
            "px-3 py-1 rounded-full text-sm font-medium",
            isPositive 
              ? "bg-gain/20 text-gain border border-gain/30" 
              : "bg-loss/20 text-loss border border-loss/30"
          )}>
            {isPositive ? "+" : ""}{changePercent.toFixed(2)}%
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="text-3xl font-bold text-foreground">
            ${price.toFixed(2)}
          </div>
          <div className={cn(
            "text-lg font-medium",
            isPositive ? "text-gain" : "text-loss"
          )}>
            {isPositive ? "+" : ""}${Math.abs(change).toFixed(2)}
          </div>
        </div>
        
        {(volume || marketCap) && (
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border/30">
            {volume && (
              <div>
                <p className="text-muted-foreground text-sm">Volume</p>
                <p className="font-medium">{volume.toLocaleString()}</p>
              </div>
            )}
            {marketCap && (
              <div>
                <p className="text-muted-foreground text-sm">Market Cap</p>
                <p className="font-medium">{marketCap}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}