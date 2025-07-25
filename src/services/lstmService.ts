import * as tf from '@tensorflow/tfjs';

export interface PredictionData {
  date: string;
  prediction: number;
}

class LSTMService {
  private model: tf.LayersModel | null = null;
  private scaler: { min: number; max: number } | null = null;

  // Normalize data to 0-1 range
  private normalizeData(data: number[]): { normalized: number[]; scaler: { min: number; max: number } } {
    const min = Math.min(...data);
    const max = Math.max(...data);
    const normalized = data.map(value => (value - min) / (max - min));
    return { normalized, scaler: { min, max } };
  }

  // Denormalize data back to original range
  private denormalizeData(normalizedData: number[], scaler: { min: number; max: number }): number[] {
    return normalizedData.map(value => value * (scaler.max - scaler.min) + scaler.min);
  }

  // Create sequences for LSTM training
  private createSequences(data: number[], lookback: number): { X: number[][]; y: number[] } {
    const X: number[][] = [];
    const y: number[] = [];
    
    for (let i = lookback; i < data.length; i++) {
      X.push(data.slice(i - lookback, i));
      y.push(data[i]);
    }
    
    return { X, y };
  }

  // Build LSTM model
  private buildModel(inputShape: number): tf.LayersModel {
    const model = tf.sequential({
      layers: [
        tf.layers.lstm({
          units: 50,
          returnSequences: true,
          inputShape: [inputShape, 1]
        }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.lstm({
          units: 50,
          returnSequences: false
        }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.dense({ units: 25 }),
        tf.layers.dense({ units: 1 })
      ]
    });

    model.compile({
      optimizer: tf.train.adam(0.001),
      loss: 'meanSquaredError',
      metrics: ['mae']
    });

    return model;
  }

  // Train the LSTM model
  async trainModel(prices: number[], epochs: number = 50, lookback: number = 10): Promise<void> {
    try {
      // Normalize the data
      const { normalized, scaler } = this.normalizeData(prices);
      this.scaler = scaler;

      // Create sequences
      const { X, y } = this.createSequences(normalized, lookback);

      if (X.length === 0) {
        throw new Error('Not enough data to train the model');
      }

      // Convert to tensors
      const xTensor = tf.tensor3d(X.map(seq => seq.map(val => [val])));
      const yTensor = tf.tensor2d(y, [y.length, 1]);

      // Build model
      this.model = this.buildModel(lookback);

      // Train the model
      await this.model.fit(xTensor, yTensor, {
        epochs,
        batchSize: 32,
        validationSplit: 0.2,
        verbose: 0, // Set to 1 for training progress
        callbacks: {
          onEpochEnd: (epoch, logs) => {
            if (epoch % 10 === 0) {
              console.log(`Epoch ${epoch}: loss = ${logs?.loss?.toFixed(4)}`);
            }
          }
        }
      });

      // Clean up tensors
      xTensor.dispose();
      yTensor.dispose();

    } catch (error) {
      console.error('Error training LSTM model:', error);
      throw error;
    }
  }

  // Make predictions
  async predict(prices: number[], lookback: number = 10, futureDays: number = 7): Promise<PredictionData[]> {
    if (!this.model || !this.scaler) {
      throw new Error('Model not trained yet');
    }

    try {
      // Normalize the input data using the same scaler
      const normalizedPrices = prices.map(price => 
        (price - this.scaler!.min) / (this.scaler!.max - this.scaler!.min)
      );

      const predictions: number[] = [];
      let currentSequence = normalizedPrices.slice(-lookback);

      // Generate predictions for future days
      for (let i = 0; i < futureDays; i++) {
        const inputTensor = tf.tensor3d([currentSequence.map(val => [val])]);
        const prediction = this.model.predict(inputTensor) as tf.Tensor;
        const predictionValue = await prediction.data();
        
        predictions.push(predictionValue[0]);
        
        // Update sequence for next prediction
        currentSequence = [...currentSequence.slice(1), predictionValue[0]];
        
        // Clean up tensors
        inputTensor.dispose();
        prediction.dispose();
      }

      // Denormalize predictions
      const denormalizedPredictions = this.denormalizeData(predictions, this.scaler);

      // Create prediction data with future dates
      const predictionData: PredictionData[] = [];
      const lastDate = new Date();
      
      for (let i = 0; i < denormalizedPredictions.length; i++) {
        const futureDate = new Date(lastDate);
        futureDate.setDate(lastDate.getDate() + i + 1);
        
        predictionData.push({
          date: futureDate.toISOString().split('T')[0],
          prediction: parseFloat(denormalizedPredictions[i].toFixed(2))
        });
      }

      return predictionData;

    } catch (error) {
      console.error('Error making predictions:', error);
      throw error;
    }
  }

  // Dispose of the model to free memory
  dispose(): void {
    if (this.model) {
      this.model.dispose();
      this.model = null;
    }
    this.scaler = null;
  }
}

export const lstmService = new LSTMService();