"""
Automated Insights & Anomaly Detection
Automatically detect patterns, trends, and anomalies

SEPARATION OF CONCERNS: Automated analysis only
"""

import pandas as pd
import numpy as np
from scipy import stats


class AutoInsights:
    """Automatically generate insights from data"""
    
    @staticmethod
    def generate_insights(df):
        """
        Generate automated insights from DataFrame
        
        Returns:
        --------
        insights : dict
            Dictionary of insights
        """
        insights = {
            'summary': [],
            'trends': [],
            'anomalies': [],
            'correlations': [],
            'recommendations': []
        }
        
        # Basic summary insights
        insights['summary'].append(f"Dataset contains {len(df):,} rows and {len(df.columns)} columns")
        
        # Missing data insights
        missing = df.isnull().sum()
        critical_missing = missing[missing > len(df) * 0.5]
        if len(critical_missing) > 0:
            insights['summary'].append(f"⚠️ {len(critical_missing)} columns have >50% missing data")
            insights['recommendations'].append("Consider removing columns with excessive missing data")
        
        # Numeric column insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights['summary'].append(f"Found {len(numeric_cols)} numeric columns for analysis")
            
            # Find columns with high variance
            for col in numeric_cols:
                if df[col].std() / df[col].mean() > 1 if df[col].mean() != 0 else False:
                    insights['trends'].append(f"Column '{col}' shows high variance (CV > 1)")
        
        # Categorical insights
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.5:
                insights['summary'].append(f"Column '{col}' has high cardinality ({df[col].nunique()} unique values)")
        
        # Duplicate insights
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            insights['summary'].append(f"⚠️ Found {duplicates:,} duplicate rows ({duplicates/len(df)*100:.1f}%)")
            insights['recommendations'].append("Consider removing duplicate rows for data integrity")
        
        # Correlation insights (top 3)
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        high_corr.append({
                            'col1': corr_matrix.columns[i],
                            'col2': corr_matrix.columns[j],
                            'corr': corr_matrix.iloc[i, j]
                        })
            
            high_corr = sorted(high_corr, key=lambda x: abs(x['corr']), reverse=True)[:3]
            for item in high_corr:
                insights['correlations'].append(
                    f"Strong correlation between '{item['col1']}' and '{item['col2']}' ({item['corr']:.2f})"
                )
        
        return insights
    
    @staticmethod
    def detect_outliers(df, column, method='iqr'):
        """
        Detect outliers in a column
        
        Parameters:
        -----------
        df : DataFrame
            Input data
        column : str
            Column to check
        method : str
            'iqr' or 'zscore'
        
        Returns:
        --------
        outliers_df : DataFrame
            Rows containing outliers
        outlier_info : dict
            Outlier statistics
        """
        try:
            if method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                
                info = {
                    'method': 'IQR',
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'num_outliers': len(outliers),
                    'pct_outliers': len(outliers) / len(df) * 100
                }
            
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(df[column].dropna()))
                threshold = 3
                outlier_indices = np.where(z_scores > threshold)[0]
                outliers = df.iloc[outlier_indices]
                
                info = {
                    'method': 'Z-Score',
                    'threshold': threshold,
                    'num_outliers': len(outliers),
                    'pct_outliers': len(outliers) / len(df) * 100
                }
            
            return outliers, info, None
        
        except Exception as e:
            return None, None, str(e)
    
    @staticmethod
    def detect_anomalies_timeseries(df, date_col, value_col, window=7):
        """
        Detect anomalies in time series data
        
        Parameters:
        -----------
        df : DataFrame
            Time series data
        date_col : str
            Date column
        value_col : str
            Value column to analyze
        window : int
            Rolling window size
        
        Returns:
        --------
        anomalies_df : DataFrame
            Detected anomalies
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            df_copy = df_copy.sort_values(date_col)
            
            # Calculate rolling mean and std
            df_copy['rolling_mean'] = df_copy[value_col].rolling(window=window).mean()
            df_copy['rolling_std'] = df_copy[value_col].rolling(window=window).std()
            
            # Define anomaly threshold (3 standard deviations)
            df_copy['upper_bound'] = df_copy['rolling_mean'] + (3 * df_copy['rolling_std'])
            df_copy['lower_bound'] = df_copy['rolling_mean'] - (3 * df_copy['rolling_std'])
            
            # Identify anomalies
            df_copy['is_anomaly'] = (
                (df_copy[value_col] > df_copy['upper_bound']) |
                (df_copy[value_col] < df_copy['lower_bound'])
            )
            
            anomalies = df_copy[df_copy['is_anomaly'] == True]
            
            return anomalies, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def identify_trends(df, date_col, value_col):
        """
        Identify trends in time series
        
        Returns:
        --------
        trend_info : dict
            Trend analysis results
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            df_copy = df_copy.sort_values(date_col).reset_index(drop=True)
            
            # Calculate trend using linear regression
            x = np.arange(len(df_copy))
            y = df_copy[value_col].values
            
            # Remove NaN values
            mask = ~np.isnan(y)
            x = x[mask]
            y = y[mask]
            
            if len(x) > 1:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                trend_info = {
                    'slope': slope,
                    'direction': 'Increasing' if slope > 0 else 'Decreasing',
                    'strength': abs(r_value),
                    'r_squared': r_value ** 2,
                    'p_value': p_value,
                    'significant': p_value < 0.05,
                    'interpretation': AutoInsights._interpret_trend(slope, r_value, p_value)
                }
                
                return trend_info, None
            else:
                return None, "Not enough data points for trend analysis"
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def _interpret_trend(slope, r_value, p_value):
        """Interpret trend results"""
        direction = "increasing" if slope > 0 else "decreasing"
        strength = "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"
        significance = "statistically significant" if p_value < 0.05 else "not statistically significant"
        
        return f"The data shows a {strength} {direction} trend ({significance}, p={p_value:.4f})"
