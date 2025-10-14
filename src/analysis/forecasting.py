"""
Time Series Forecasting
Predict future values using statistical methods

SEPARATION OF CONCERNS: Forecasting analysis only
"""

import pandas as pd
import numpy as np
from scipy import stats


class TimeSeriesForecasting:
    """Time series forecasting methods"""
    
    @staticmethod
    def simple_moving_average(df, date_col, value_col, window=7, periods=30):
        """
        Simple Moving Average forecast
        
        Parameters:
        -----------
        df : DataFrame
            Historical data
        date_col : str
            Date column
        value_col : str
            Value column to forecast
        window : int
            Moving average window
        periods : int
            Number of periods to forecast
        
        Returns:
        --------
        forecast_df : DataFrame
            Historical + forecast data
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            df_copy = df_copy.sort_values(date_col)
            
            # Calculate moving average
            df_copy['forecast'] = df_copy[value_col].rolling(window=window).mean()
            
            # Generate future dates
            last_date = df_copy[date_col].max()
            freq = pd.infer_freq(df_copy[date_col])
            if freq is None:
                freq = 'D'  # Default to daily
            
            future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
            
            # Use last moving average as forecast
            last_ma = df_copy['forecast'].iloc[-1]
            
            forecast_data = pd.DataFrame({
                date_col: future_dates,
                value_col: np.nan,
                'forecast': last_ma
            })
            
            result = pd.concat([df_copy, forecast_data], ignore_index=True)
            
            return result, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def linear_trend_forecast(df, date_col, value_col, periods=30):
        """
        Linear trend forecast using regression
        
        Parameters:
        -----------
        df : DataFrame
            Historical data
        date_col : str
            Date column
        value_col : str
            Value column to forecast
        periods : int
            Number of periods to forecast
        
        Returns:
        --------
        forecast_df : DataFrame
            Historical + forecast data
        trend_info : dict
            Trend statistics
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            df_copy = df_copy.sort_values(date_col).reset_index(drop=True)
            
            # Prepare data for regression
            x = np.arange(len(df_copy))
            y = df_copy[value_col].values
            
            # Remove NaN
            mask = ~np.isnan(y)
            x_clean = x[mask]
            y_clean = y[mask]
            
            # Fit linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
            
            # Calculate fitted values
            df_copy['forecast'] = slope * x + intercept
            
            # Generate future forecast
            last_date = df_copy[date_col].max()
            freq = pd.infer_freq(df_copy[date_col])
            if freq is None:
                freq = 'D'
            
            future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
            future_x = np.arange(len(df_copy), len(df_copy) + periods)
            future_forecast = slope * future_x + intercept
            
            forecast_data = pd.DataFrame({
                date_col: future_dates,
                value_col: np.nan,
                'forecast': future_forecast
            })
            
            result = pd.concat([df_copy, forecast_data], ignore_index=True)
            
            trend_info = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'direction': 'Increasing' if slope > 0 else 'Decreasing',
                'daily_change': slope
            }
            
            return result, trend_info, None
        
        except Exception as e:
            return None, None, str(e)
    
    @staticmethod
    def exponential_smoothing(df, date_col, value_col, alpha=0.3, periods=30):
        """
        Exponential smoothing forecast
        
        Parameters:
        -----------
        df : DataFrame
            Historical data
        date_col : str
            Date column
        value_col : str
            Value column to forecast
        alpha : float
            Smoothing parameter (0-1)
        periods : int
            Number of periods to forecast
        
        Returns:
        --------
        forecast_df : DataFrame
            Historical + forecast data
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            df_copy = df_copy.sort_values(date_col).reset_index(drop=True)
            
            # Calculate exponential smoothing
            forecast = [df_copy[value_col].iloc[0]]  # Start with first value
            
            for i in range(1, len(df_copy)):
                if pd.notna(df_copy[value_col].iloc[i]):
                    forecast.append(alpha * df_copy[value_col].iloc[i] + (1 - alpha) * forecast[-1])
                else:
                    forecast.append(forecast[-1])
            
            df_copy['forecast'] = forecast
            
            # Generate future forecast
            last_date = df_copy[date_col].max()
            freq = pd.infer_freq(df_copy[date_col])
            if freq is None:
                freq = 'D'
            
            future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
            last_forecast = forecast[-1]
            
            forecast_data = pd.DataFrame({
                date_col: future_dates,
                value_col: np.nan,
                'forecast': last_forecast
            })
            
            result = pd.concat([df_copy, forecast_data], ignore_index=True)
            
            return result, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def calculate_forecast_accuracy(actual, predicted):
        """
        Calculate forecast accuracy metrics
        
        Parameters:
        -----------
        actual : array-like
            Actual values
        predicted : array-like
            Predicted values
        
        Returns:
        --------
        metrics : dict
            Accuracy metrics
        """
        try:
            actual = np.array(actual)
            predicted = np.array(predicted)
            
            # Remove NaN values
            mask = ~(np.isnan(actual) | np.isnan(predicted))
            actual = actual[mask]
            predicted = predicted[mask]
            
            if len(actual) == 0:
                return None, "No valid data points for accuracy calculation"
            
            # Calculate metrics
            mae = np.mean(np.abs(actual - predicted))
            mse = np.mean((actual - predicted) ** 2)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs((actual - predicted) / actual)) * 100 if not np.any(actual == 0) else np.nan
            
            metrics = {
                'MAE': mae,
                'MSE': mse,
                'RMSE': rmse,
                'MAPE': mape
            }
            
            return metrics, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def seasonal_decomposition_simple(df, date_col, value_col, period=7):
        """
        Simple seasonal decomposition
        
        Parameters:
        -----------
        df : DataFrame
            Time series data
        date_col : str
            Date column
        value_col : str
            Value column
        period : int
            Seasonal period (e.g., 7 for weekly)
        
        Returns:
        --------
        decomposed : DataFrame
            Trend, seasonal, and residual components
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            df_copy = df_copy.sort_values(date_col).reset_index(drop=True)
            
            # Calculate trend (moving average)
            df_copy['trend'] = df_copy[value_col].rolling(window=period, center=True).mean()
            
            # Calculate seasonal component
            df_copy['detrended'] = df_copy[value_col] - df_copy['trend']
            seasonal = df_copy.groupby(df_copy.index % period)['detrended'].transform('mean')
            df_copy['seasonal'] = seasonal
            
            # Calculate residual
            df_copy['residual'] = df_copy[value_col] - df_copy['trend'] - df_copy['seasonal']
            
            return df_copy, None
        
        except Exception as e:
            return None, str(e)
