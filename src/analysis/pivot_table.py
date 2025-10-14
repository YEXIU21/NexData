"""
Pivot Table Generator
Create interactive pivot tables from data

SEPARATION OF CONCERNS: Pivot table creation only
"""

import pandas as pd
import numpy as np


class PivotTableGenerator:
    """Generate pivot tables from DataFrames"""
    
    @staticmethod
    def create_pivot(df, index_cols, column_cols, value_col, agg_func='sum'):
        """
        Create a pivot table
        
        Parameters:
        -----------
        df : DataFrame
            Input data
        index_cols : list
            Columns to use as index (rows)
        column_cols : list
            Columns to use as columns
        value_col : str
            Column to aggregate
        agg_func : str
            Aggregation function ('sum', 'mean', 'count', 'min', 'max')
        
        Returns:
        --------
        pivot_df : DataFrame
            Pivot table result
        """
        try:
            # Handle multiple index columns
            if len(index_cols) == 0:
                index_cols = None
            elif len(index_cols) == 1:
                index_cols = index_cols[0]
            
            # Handle multiple column columns
            if len(column_cols) == 0:
                column_cols = None
            elif len(column_cols) == 1:
                column_cols = column_cols[0]
            
            # Create pivot table
            pivot_df = pd.pivot_table(
                df,
                values=value_col,
                index=index_cols,
                columns=column_cols,
                aggfunc=agg_func,
                fill_value=0
            )
            
            return pivot_df, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_aggregation_functions():
        """Get list of available aggregation functions"""
        return {
            'sum': 'Sum',
            'mean': 'Average',
            'count': 'Count',
            'min': 'Minimum',
            'max': 'Maximum',
            'median': 'Median',
            'std': 'Standard Deviation'
        }
    
    @staticmethod
    def create_cross_tab(df, row_col, col_col, normalize=False):
        """
        Create a cross-tabulation (frequency table)
        
        Parameters:
        -----------
        df : DataFrame
            Input data
        row_col : str
            Column for rows
        col_col : str
            Column for columns
        normalize : bool
            Normalize to show percentages
        
        Returns:
        --------
        crosstab_df : DataFrame
            Cross-tabulation result
        """
        try:
            if normalize:
                crosstab_df = pd.crosstab(
                    df[row_col],
                    df[col_col],
                    normalize='all'
                ) * 100
            else:
                crosstab_df = pd.crosstab(
                    df[row_col],
                    df[col_col]
                )
            
            return crosstab_df, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def pivot_summary(df, group_by_col, agg_cols, agg_funcs=['sum', 'mean', 'count']):
        """
        Create a summary table with multiple aggregations
        
        Parameters:
        -----------
        df : DataFrame
            Input data
        group_by_col : str
            Column to group by
        agg_cols : list
            Columns to aggregate
        agg_funcs : list
            Aggregation functions to apply
        
        Returns:
        --------
        summary_df : DataFrame
            Summary table
        """
        try:
            # Create aggregation dictionary
            agg_dict = {col: agg_funcs for col in agg_cols}
            
            # Group and aggregate
            summary_df = df.groupby(group_by_col).agg(agg_dict).round(2)
            
            # Flatten column names
            summary_df.columns = ['_'.join(col).strip() for col in summary_df.columns.values]
            summary_df = summary_df.reset_index()
            
            return summary_df, None
        
        except Exception as e:
            return None, str(e)
