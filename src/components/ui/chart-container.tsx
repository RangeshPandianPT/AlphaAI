import { Card } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { cn } from "@/lib/utils";

interface ChartPoint {
  date: string;
  price: number;
  prediction?: number;
}

interface ChartContainerProps {
  data: ChartPoint[];
  title: string;
  showPrediction?: boolean;
  className?: string;
}

export function ChartContainer({ data, title, showPrediction = false, className }: ChartContainerProps) {
  const predictionStart = data.findIndex(point => point.prediction !== undefined);
  
  return (
    <Card className={cn(
      "bg-gradient-card border-border/50 backdrop-blur-sm p-6 shadow-chart",
      className
    )}>
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
              <XAxis 
                dataKey="date" 
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                domain={['dataMin - 5', 'dataMax + 5']}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                  color: "hsl(var(--card-foreground))"
                }}
                labelStyle={{ color: "hsl(var(--muted-foreground))" }}
              />
              
              <Line
                type="monotone"
                dataKey="price"
                stroke="hsl(var(--chart-primary))"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: "hsl(var(--chart-primary))" }}
              />
              
              {showPrediction && (
                <>
                  {predictionStart > 0 && (
                    <ReferenceLine 
                      x={data[predictionStart]?.date} 
                      stroke="hsl(var(--muted-foreground))" 
                      strokeDasharray="5 5"
                      opacity={0.6}
                    />
                  )}
                  <Line
                    type="monotone"
                    dataKey="prediction"
                    stroke="hsl(var(--chart-secondary))"
                    strokeWidth={2}
                    strokeDasharray="8 4"
                    dot={false}
                    activeDot={{ r: 4, fill: "hsl(var(--chart-secondary))" }}
                    connectNulls={false}
                  />
                </>
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {showPrediction && (
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-0.5 bg-chart-primary rounded"></div>
              <span className="text-muted-foreground">Historical Price</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-0.5 bg-chart-secondary rounded border-dashed border border-chart-secondary"></div>
              <span className="text-muted-foreground">AI Prediction</span>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}