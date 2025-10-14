"""
Advanced Filtering System
Multi-column filtering with complex conditions

SEPARATION OF CONCERNS: Data filtering operations only
"""

import pandas as pd
import numpy as np
from datetime import datetime


class AdvancedFilter:
    """Advanced filtering capabilities"""
    
    @staticmethod
    def filter_by_conditions(df, conditions):
        """
        Filter DataFrame by multiple conditions
        
        Parameters:
        -----------
        df : DataFrame
            Input data
        conditions : list of dict
            List of condition dictionaries:
            {'column': 'col_name', 'operator': '>', 'value': 100}
        
        Returns:
        --------
        filtered_df : DataFrame
            Filtered data
        """
        try:
            result_df = df.copy()
            
            for condition in conditions:
                column = condition['column']
                operator = condition['operator']
                value = condition['value']
                
                if operator == '==':
                    result_df = result_df[result_df[column] == value]
                elif operator == '!=':
                    result_df = result_df[result_df[column] != value]
                elif operator == '>':
                    result_df = result_df[result_df[column] > value]
                elif operator == '<':
                    result_df = result_df[result_df[column] < value]
                elif operator == '>=':
                    result_df = result_df[result_df[column] >= value]
                elif operator == '<=':
                    result_df = result_df[result_df[column] <= value]
                elif operator == 'contains':
                    result_df = result_df[result_df[column].astype(str).str.contains(str(value), case=False, na=False)]
                elif operator == 'not contains':
                    result_df = result_df[~result_df[column].astype(str).str.contains(str(value), case=False, na=False)]
                elif operator == 'starts with':
                    result_df = result_df[result_df[column].astype(str).str.startswith(str(value), na=False)]
                elif operator == 'ends with':
                    result_df = result_df[result_df[column].astype(str).str.endswith(str(value), na=False)]
            
            return result_df, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def filter_by_date_range(df, date_column, start_date, end_date):
        """Filter by date range"""
        try:
            df_copy = df.copy()
            df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
            
            filtered_df = df_copy[
                (df_copy[date_column] >= start_date) &
                (df_copy[date_column] <= end_date)
            ]
            
            return filtered_df, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def filter_top_n(df, column, n=10, ascending=False):
        """Get top N rows by column value"""
        try:
            filtered_df = df.nlargest(n, column) if not ascending else df.nsmallest(n, column)
            return filtered_df, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def filter_by_percentile(df, column, lower_percentile=0, upper_percentile=100):
        """Filter by percentile range"""
        try:
            lower_bound = df[column].quantile(lower_percentile / 100)
            upper_bound = df[column].quantile(upper_percentile / 100)
            
            filtered_df = df[
                (df[column] >= lower_bound) &
                (df[column] <= upper_bound)
            ]
            
            return filtered_df, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_operators():
        """Get list of available operators"""
        return {
            'numeric': ['==', '!=', '>', '<', '>=', '<='],
            'text': ['==', '!=', 'contains', 'not contains', 'starts with', 'ends with'],
            'all': ['==', '!=', '>', '<', '>=', '<=', 'contains', 'not contains', 'starts with', 'ends with']
        }
