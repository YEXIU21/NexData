"""
Data Comparison Tool
Compare two datasets side-by-side

SEPARATION OF CONCERNS: Data comparison operations only
"""

import pandas as pd
import numpy as np


class DataComparison:
    """Compare two DataFrames"""
    
    @staticmethod
    def compare_dataframes(df1, df2, join_key=None):
        """
        Compare two DataFrames
        
        Parameters:
        -----------
        df1 : DataFrame
            First dataset
        df2 : DataFrame
            Second dataset
        join_key : str, optional
            Column to join on (if provided)
        
        Returns:
        --------
        comparison_results : dict
            Dictionary with comparison results
        """
        results = {}
        
        # Basic comparison
        results['df1_shape'] = df1.shape
        results['df2_shape'] = df2.shape
        results['same_shape'] = df1.shape == df2.shape
        
        # Column comparison
        df1_cols = set(df1.columns)
        df2_cols = set(df2.columns)
        results['common_columns'] = list(df1_cols & df2_cols)
        results['only_in_df1'] = list(df1_cols - df2_cols)
        results['only_in_df2'] = list(df2_cols - df1_cols)
        
        # Data type comparison
        if results['common_columns']:
            dtype_diff = {}
            for col in results['common_columns']:
                if str(df1[col].dtype) != str(df2[col].dtype):
                    dtype_diff[col] = {
                        'df1': str(df1[col].dtype),
                        'df2': str(df2[col].dtype)
                    }
            results['dtype_differences'] = dtype_diff
        
        # If join key provided, compare matched rows
        if join_key and join_key in results['common_columns']:
            merged = pd.merge(
                df1,
                df2,
                on=join_key,
                how='outer',
                suffixes=('_df1', '_df2'),
                indicator=True
            )
            
            results['rows_only_in_df1'] = len(merged[merged['_merge'] == 'left_only'])
            results['rows_only_in_df2'] = len(merged[merged['_merge'] == 'right_only'])
            results['rows_in_both'] = len(merged[merged['_merge'] == 'both'])
            
            # Find value differences in common rows
            value_diffs = []
            for col in results['common_columns']:
                if col == join_key:
                    continue
                col_df1 = f"{col}_df1"
                col_df2 = f"{col}_df2"
                if col_df1 in merged.columns and col_df2 in merged.columns:
                    diff_mask = merged[col_df1] != merged[col_df2]
                    num_diffs = diff_mask.sum()
                    if num_diffs > 0:
                        value_diffs.append({
                            'column': col,
                            'num_differences': num_diffs
                        })
            
            results['value_differences'] = value_diffs
        
        return results
    
    @staticmethod
    def find_duplicates(df1, df2, subset=None):
        """Find duplicate rows between two DataFrames"""
        try:
            # Concatenate dataframes
            combined = pd.concat([df1, df2], ignore_index=True)
            
            # Find duplicates
            if subset:
                duplicates = combined[combined.duplicated(subset=subset, keep=False)]
            else:
                duplicates = combined[combined.duplicated(keep=False)]
            
            return duplicates, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def merge_datasets(df1, df2, join_key, how='inner'):
        """
        Merge two datasets
        
        Parameters:
        -----------
        df1, df2 : DataFrame
            Datasets to merge
        join_key : str or list
            Column(s) to join on
        how : str
            'inner', 'outer', 'left', 'right'
        
        Returns:
        --------
        merged_df : DataFrame
            Merged result
        """
        try:
            merged = pd.merge(df1, df2, on=join_key, how=how, suffixes=('_df1', '_df2'))
            return merged, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_summary_comparison(df1, df2):
        """Get statistical summary comparison"""
        try:
            # Get numeric columns only
            numeric_df1 = df1.select_dtypes(include=[np.number])
            numeric_df2 = df2.select_dtypes(include=[np.number])
            
            # Get common numeric columns
            common_numeric = list(set(numeric_df1.columns) & set(numeric_df2.columns))
            
            if not common_numeric:
                return None, "No common numeric columns to compare"
            
            comparison = pd.DataFrame()
            for col in common_numeric:
                comparison.loc[col, 'Mean_DF1'] = numeric_df1[col].mean()
                comparison.loc[col, 'Mean_DF2'] = numeric_df2[col].mean()
                comparison.loc[col, 'Diff'] = numeric_df2[col].mean() - numeric_df1[col].mean()
                comparison.loc[col, 'Pct_Change'] = (
                    (numeric_df2[col].mean() - numeric_df1[col].mean()) / 
                    numeric_df1[col].mean() * 100
                ) if numeric_df1[col].mean() != 0 else 0
            
            return comparison.round(2), None
        
        except Exception as e:
            return None, str(e)
