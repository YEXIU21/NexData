"""
Statistical Analysis Operations
All statistical analysis functions

SEPARATION OF CONCERNS: Only statistical analysis logic
"""

import pandas as pd
import numpy as np


class StatisticalAnalyzer:
    """Handles statistical analysis operations"""
    
    @staticmethod
    def descriptive_stats(df):
        """Get descriptive statistics"""
        return df.describe()
    
    @staticmethod
    def correlation_matrix(df):
        """Calculate correlation matrix for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return None, "Need at least 2 numeric columns"
        return df[numeric_cols].corr(), None
    
    @staticmethod
    def column_info(df, column):
        """Get detailed info about a column"""
        info = {
            'dtype': str(df[column].dtype),
            'non_null': df[column].notna().sum(),
            'null_count': df[column].isna().sum(),
            'unique': df[column].nunique(),
            'value_counts': df[column].value_counts().head(10)
        }
        
        if pd.api.types.is_numeric_dtype(df[column]):
            info['mean'] = df[column].mean()
            info['median'] = df[column].median()
            info['std'] = df[column].std()
            info['min'] = df[column].min()
            info['max'] = df[column].max()
        
        return info
    
    @staticmethod
    def data_quality_report(df):
        """Generate data quality report"""
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': len(df.select_dtypes(include=['object']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime64']).columns)
        }
        return report
    
    @staticmethod
    def missing_value_analysis(df):
        """Analyze missing values per column"""
        missing = pd.DataFrame({
            'column': df.columns,
            'missing_count': df.isnull().sum().values,
            'missing_percentage': (df.isnull().sum().values / len(df) * 100)
        })
        return missing[missing['missing_count'] > 0].sort_values('missing_count', ascending=False)


class TimeSeriesAnalyzer:
    """Handles time series analysis"""
    
    @staticmethod
    def prepare_time_series(df, date_column, value_column):
        """Prepare data for time series analysis"""
        df_ts = df.copy()
        df_ts[date_column] = pd.to_datetime(df_ts[date_column])
        df_ts = df_ts.sort_values(date_column)
        return df_ts
    
    @staticmethod
    def calculate_trends(df, date_column, value_column):
        """Calculate trends and moving averages"""
        df_trend = df.copy()
        df_trend['MA_7'] = df_trend[value_column].rolling(window=7).mean()
        df_trend['MA_30'] = df_trend[value_column].rolling(window=30).mean()
        return df_trend
    
    @staticmethod
    def aggregate_by_period(df, date_column, value_column, period='M'):
        """Aggregate data by time period (D=daily, W=weekly, M=monthly)"""
        df_agg = df.copy()
        df_agg.set_index(date_column, inplace=True)
        return df_agg[value_column].resample(period).sum()
