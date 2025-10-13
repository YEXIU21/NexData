"""
Data Cleaning Operations
All data cleaning and preprocessing functions

SEPARATION OF CONCERNS: Only data cleaning logic
"""

import pandas as pd
import numpy as np


class DataCleaner:
    """Handles all data cleaning operations"""
    
    @staticmethod
    def remove_duplicates(df):
        """Remove duplicate rows"""
        before = len(df)
        df_clean = df.drop_duplicates()
        removed = before - len(df_clean)
        return df_clean, removed
    
    @staticmethod
    def handle_missing_drop(df):
        """Drop rows with missing values"""
        before = len(df)
        df_clean = df.dropna()
        removed = before - len(df_clean)
        return df_clean, removed
    
    @staticmethod
    def handle_missing_mean(df):
        """Fill missing with mean (numeric columns)"""
        df_clean = df.copy()
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        return df_clean
    
    @staticmethod
    def handle_missing_median(df):
        """Fill missing with median (numeric columns)"""
        df_clean = df.copy()
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
        return df_clean
    
    @staticmethod
    def handle_missing_mode(df):
        """Fill missing with mode (all columns)"""
        df_clean = df.copy()
        for col in df_clean.columns:
            if df_clean[col].isnull().sum() > 0:
                mode_val = df_clean[col].mode()
                if len(mode_val) > 0:
                    df_clean[col].fillna(mode_val[0], inplace=True)
        return df_clean
    
    @staticmethod
    def handle_missing_ffill(df):
        """Forward fill missing values"""
        return df.fillna(method='ffill')
    
    @staticmethod
    def handle_missing_bfill(df):
        """Backward fill missing values"""
        return df.fillna(method='bfill')
    
    @staticmethod
    def remove_outliers_iqr(df):
        """Remove outliers using IQR method"""
        df_clean = df.copy()
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        
        before = len(df_clean)
        for col in numeric_cols:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
        
        removed = before - len(df_clean)
        return df_clean, removed
    
    @staticmethod
    def normalize_minmax(df, columns):
        """Min-Max normalization (0-1)"""
        df_norm = df.copy()
        for col in columns:
            if pd.api.types.is_numeric_dtype(df_norm[col]):
                min_val = df_norm[col].min()
                max_val = df_norm[col].max()
                if max_val != min_val:
                    df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
        return df_norm
    
    @staticmethod
    def normalize_zscore(df, columns):
        """Z-score normalization (mean=0, std=1)"""
        df_norm = df.copy()
        for col in columns:
            if pd.api.types.is_numeric_dtype(df_norm[col]):
                mean_val = df_norm[col].mean()
                std_val = df_norm[col].std()
                if std_val != 0:
                    df_norm[col] = (df_norm[col] - mean_val) / std_val
        return df_norm


class DataTransformer:
    """Handles data type conversions and transformations"""
    
    @staticmethod
    def convert_to_numeric(df, column):
        """Convert column to numeric"""
        df_converted = df.copy()
        df_converted[column] = pd.to_numeric(df_converted[column], errors='coerce')
        return df_converted
    
    @staticmethod
    def convert_to_integer(df, column):
        """Convert column to integer"""
        df_converted = df.copy()
        df_converted[column] = pd.to_numeric(df_converted[column], errors='coerce').astype('Int64')
        return df_converted
    
    @staticmethod
    def convert_to_string(df, column):
        """Convert column to string"""
        df_converted = df.copy()
        df_converted[column] = df_converted[column].astype(str)
        return df_converted
    
    @staticmethod
    def convert_to_datetime(df, column):
        """Convert column to datetime"""
        df_converted = df.copy()
        df_converted[column] = pd.to_datetime(df_converted[column], errors='coerce')
        return df_converted
    
    @staticmethod
    def sort_by_column(df, column, ascending=True):
        """Sort dataframe by column"""
        return df.sort_values(by=column, ascending=ascending)
