"""
Cleaning Service
Handles all data cleaning operations
Extracted from main_window.py to improve code organization
"""

import pandas as pd
import numpy as np
import re
from tkinter import messagebox


class CleaningService:
    """Service class for data cleaning operations"""
    
    def __init__(self):
        pass
    
    def remove_duplicates(self, df, subset=None, keep='first'):
        """
        Remove duplicate rows from dataframe
        
        Args:
            df: DataFrame to clean
            subset: List of columns to consider for duplicates (None = all columns)
            keep: 'first', 'last', or False (remove all duplicates)
            
        Returns:
            tuple: (cleaned_df, num_duplicates_removed)
        """
        try:
            initial_count = len(df)
            
            if subset:
                cleaned_df = df.drop_duplicates(subset=subset, keep=keep)
            else:
                cleaned_df = df.drop_duplicates(keep=keep)
            
            duplicates_removed = initial_count - len(cleaned_df)
            
            return cleaned_df, duplicates_removed
            
        except Exception as e:
            raise ValueError(f"Error removing duplicates: {str(e)}")
    
    def handle_missing_values(self, df, column, method='drop', fill_value=None):
        """
        Handle missing values in a column
        
        Args:
            df: DataFrame to clean
            column: Column name to handle
            method: 'drop', 'fill_mean', 'fill_median', 'fill_mode', 'fill_forward', 'fill_backward', 'fill_value'
            fill_value: Value to fill if method is 'fill_value'
            
        Returns:
            DataFrame: Cleaned dataframe
        """
        try:
            df_copy = df.copy()
            
            if method == 'drop':
                df_copy = df_copy.dropna(subset=[column])
            elif method == 'fill_mean':
                df_copy[column] = df_copy[column].fillna(df_copy[column].mean())
            elif method == 'fill_median':
                df_copy[column] = df_copy[column].fillna(df_copy[column].median())
            elif method == 'fill_mode':
                mode_value = df_copy[column].mode()[0] if len(df_copy[column].mode()) > 0 else 0
                df_copy[column] = df_copy[column].fillna(mode_value)
            elif method == 'fill_forward':
                df_copy[column] = df_copy[column].fillna(method='ffill')
            elif method == 'fill_backward':
                df_copy[column] = df_copy[column].fillna(method='bfill')
            elif method == 'fill_value' and fill_value is not None:
                df_copy[column] = df_copy[column].fillna(fill_value)
            else:
                raise ValueError(f"Invalid method: {method}")
            
            return df_copy
            
        except Exception as e:
            raise ValueError(f"Error handling missing values: {str(e)}")
    
    def smart_fill_missing(self, df, target_column, id_column):
        """
        Smart fill missing values by matching IDs
        
        Args:
            df: DataFrame to clean
            target_column: Column with missing values to fill
            id_column: ID column to match on
            
        Returns:
            tuple: (cleaned_df, num_filled)
        """
        try:
            df_copy = df.copy()
            filled_count = 0
            
            # Get rows with missing values
            missing_mask = df_copy[target_column].isnull()
            
            for idx in df_copy[missing_mask].index:
                id_value = df_copy.at[idx, id_column]
                
                # Find matching rows with same ID that have the value
                matching_rows = df_copy[
                    (df_copy[id_column] == id_value) & 
                    (df_copy[target_column].notnull())
                ]
                
                if len(matching_rows) > 0:
                    # Use the most common value for this ID
                    fill_value = matching_rows[target_column].mode()[0]
                    df_copy.at[idx, target_column] = fill_value
                    filled_count += 1
            
            return df_copy, filled_count
            
        except Exception as e:
            raise ValueError(f"Error in smart fill: {str(e)}")
    
    def find_and_replace(self, df, column, find_value, replace_value, exact_match=True):
        """
        Find and replace values in a column
        
        Args:
            df: DataFrame to modify
            column: Column name
            find_value: Value to find
            replace_value: Value to replace with
            exact_match: If True, only replace exact matches
            
        Returns:
            tuple: (cleaned_df, num_replaced)
        """
        try:
            df_copy = df.copy()
            
            if exact_match:
                mask = df_copy[column] == find_value
            else:
                mask = df_copy[column].astype(str).str.contains(find_value, na=False, case=False)
            
            num_replaced = mask.sum()
            df_copy.loc[mask, column] = replace_value
            
            return df_copy, num_replaced
            
        except Exception as e:
            raise ValueError(f"Error in find and replace: {str(e)}")
    
    def standardize_text_case(self, df, columns, case_type='title'):
        """
        Standardize text case in columns
        
        Args:
            df: DataFrame to modify
            columns: List of column names
            case_type: 'upper', 'lower', 'title', 'capitalize'
            
        Returns:
            DataFrame: Modified dataframe
        """
        try:
            df_copy = df.copy()
            
            for column in columns:
                if case_type == 'upper':
                    df_copy[column] = df_copy[column].astype(str).str.upper()
                elif case_type == 'lower':
                    df_copy[column] = df_copy[column].astype(str).str.lower()
                elif case_type == 'title':
                    df_copy[column] = df_copy[column].astype(str).str.title()
                elif case_type == 'capitalize':
                    df_copy[column] = df_copy[column].astype(str).str.capitalize()
            
            return df_copy
            
        except Exception as e:
            raise ValueError(f"Error standardizing text case: {str(e)}")
    
    def remove_empty_rows_columns(self, df, remove_rows=True, remove_cols=True):
        """
        Remove empty rows and/or columns
        
        Args:
            df: DataFrame to clean
            remove_rows: If True, remove empty rows
            remove_cols: If True, remove empty columns
            
        Returns:
            tuple: (cleaned_df, rows_removed, cols_removed)
        """
        try:
            df_copy = df.copy()
            initial_rows = len(df_copy)
            initial_cols = len(df_copy.columns)
            
            if remove_rows:
                df_copy = df_copy.dropna(how='all')
            
            if remove_cols:
                df_copy = df_copy.dropna(axis=1, how='all')
            
            rows_removed = initial_rows - len(df_copy)
            cols_removed = initial_cols - len(df_copy.columns)
            
            return df_copy, rows_removed, cols_removed
            
        except Exception as e:
            raise ValueError(f"Error removing empty rows/columns: {str(e)}")
    
    def trim_all_columns(self, df):
        """
        Trim whitespace from all text columns
        
        Args:
            df: DataFrame to clean
            
        Returns:
            DataFrame: Cleaned dataframe
        """
        try:
            df_copy = df.copy()
            
            # Get text columns
            text_cols = df_copy.select_dtypes(include=['object']).columns
            
            for col in text_cols:
                # Trim whitespace
                df_copy[col] = df_copy[col].astype(str).str.strip()
                # Replace multiple spaces with single space
                df_copy[col] = df_copy[col].str.replace(r'\s+', ' ', regex=True)
            
            return df_copy
            
        except Exception as e:
            raise ValueError(f"Error trimming columns: {str(e)}")
    
    def remove_outliers(self, df, column, method='iqr', threshold=1.5):
        """
        Remove outliers from a numeric column
        
        Args:
            df: DataFrame to clean
            column: Column name
            method: 'iqr' or 'zscore'
            threshold: Threshold value (1.5 for IQR, 3 for zscore)
            
        Returns:
            tuple: (cleaned_df, num_outliers_removed)
        """
        try:
            df_copy = df.copy()
            initial_count = len(df_copy)
            
            if method == 'iqr':
                Q1 = df_copy[column].quantile(0.25)
                Q3 = df_copy[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                df_copy = df_copy[
                    (df_copy[column] >= lower_bound) & 
                    (df_copy[column] <= upper_bound)
                ]
            
            elif method == 'zscore':
                from scipy import stats
                z_scores = np.abs(stats.zscore(df_copy[column]))
                df_copy = df_copy[z_scores < threshold]
            
            outliers_removed = initial_count - len(df_copy)
            
            return df_copy, outliers_removed
            
        except Exception as e:
            raise ValueError(f"Error removing outliers: {str(e)}")
    
    def convert_data_types(self, df, column, target_type):
        """
        Convert column to target data type
        
        Args:
            df: DataFrame to modify
            column: Column name
            target_type: 'int', 'float', 'string', 'datetime', 'category'
            
        Returns:
            DataFrame: Modified dataframe
        """
        try:
            df_copy = df.copy()
            
            if target_type == 'int':
                df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce').astype('Int64')
            elif target_type == 'float':
                df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce')
            elif target_type == 'string':
                df_copy[column] = df_copy[column].astype(str)
            elif target_type == 'datetime':
                df_copy[column] = pd.to_datetime(df_copy[column], errors='coerce')
            elif target_type == 'category':
                df_copy[column] = df_copy[column].astype('category')
            
            return df_copy
            
        except Exception as e:
            raise ValueError(f"Error converting data type: {str(e)}")
    
    def standardize_dates(self, df, column, date_format='%Y-%m-%d'):
        """
        Standardize date format in a column
        
        Args:
            df: DataFrame to modify
            column: Column name
            date_format: Target date format (default: YYYY-MM-DD)
            
        Returns:
            DataFrame: Modified dataframe
        """
        try:
            df_copy = df.copy()
            
            # Convert to datetime
            df_copy[column] = pd.to_datetime(df_copy[column], errors='coerce')
            
            # Format as string
            df_copy[column] = df_copy[column].dt.strftime(date_format)
            
            return df_copy
            
        except Exception as e:
            raise ValueError(f"Error standardizing dates: {str(e)}")
    
    def remove_special_characters(self, df, columns, keep_alphanumeric=True, keep_spaces=True):
        """
        Remove special characters from text columns
        
        Args:
            df: DataFrame to modify
            columns: List of column names
            keep_alphanumeric: Keep letters and numbers
            keep_spaces: Keep spaces
            
        Returns:
            DataFrame: Modified dataframe
        """
        try:
            df_copy = df.copy()
            
            for column in columns:
                if keep_alphanumeric and keep_spaces:
                    pattern = r'[^a-zA-Z0-9\s]'
                elif keep_alphanumeric:
                    pattern = r'[^a-zA-Z0-9]'
                elif keep_spaces:
                    pattern = r'[^\s]'
                else:
                    pattern = r'[^a-zA-Z]'
                
                df_copy[column] = df_copy[column].astype(str).str.replace(pattern, '', regex=True)
            
            return df_copy
            
        except Exception as e:
            raise ValueError(f"Error removing special characters: {str(e)}")
    
    def split_column(self, df, column, delimiter, new_column_names=None):
        """
        Split a column into multiple columns
        
        Args:
            df: DataFrame to modify
            column: Column name to split
            delimiter: Delimiter to split on
            new_column_names: List of names for new columns
            
        Returns:
            DataFrame: Modified dataframe with new columns
        """
        try:
            df_copy = df.copy()
            
            # Split the column
            split_data = df_copy[column].astype(str).str.split(delimiter, expand=True)
            
            # Name the new columns
            if new_column_names and len(new_column_names) == split_data.shape[1]:
                split_data.columns = new_column_names
            else:
                split_data.columns = [f"{column}_{i+1}" for i in range(split_data.shape[1])]
            
            # Add new columns to dataframe
            df_copy = pd.concat([df_copy, split_data], axis=1)
            
            return df_copy
            
        except Exception as e:
            raise ValueError(f"Error splitting column: {str(e)}")
    
    def merge_columns(self, df, columns, new_column_name, delimiter=' '):
        """
        Merge multiple columns into one
        
        Args:
            df: DataFrame to modify
            columns: List of column names to merge
            new_column_name: Name for the merged column
            delimiter: Delimiter to use when merging
            
        Returns:
            DataFrame: Modified dataframe with merged column
        """
        try:
            df_copy = df.copy()
            
            # Merge columns
            df_copy[new_column_name] = df_copy[columns].astype(str).agg(delimiter.join, axis=1)
            
            return df_copy
            
        except Exception as e:
            raise ValueError(f"Error merging columns: {str(e)}")
