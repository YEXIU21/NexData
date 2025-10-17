"""
Analysis Service
Handles all data analysis operations
Extracted from main_window.py to improve code organization
"""

import pandas as pd
import numpy as np
from scipy import stats


class AnalysisService:
    """Service class for data analysis operations"""
    
    def __init__(self):
        pass
    
    def group_by_analysis(self, df, group_column, agg_column, agg_function='sum'):
        """
        Perform group by analysis
        
        Args:
            df: DataFrame to analyze
            group_column: Column to group by
            agg_column: Column to aggregate
            agg_function: Aggregation function ('sum', 'mean', 'count', 'min', 'max')
            
        Returns:
            DataFrame: Grouped results
        """
        try:
            if agg_function == 'sum':
                result = df.groupby(group_column)[agg_column].sum().reset_index()
            elif agg_function == 'mean':
                result = df.groupby(group_column)[agg_column].mean().reset_index()
            elif agg_function == 'count':
                result = df.groupby(group_column)[agg_column].count().reset_index()
            elif agg_function == 'min':
                result = df.groupby(group_column)[agg_column].min().reset_index()
            elif agg_function == 'max':
                result = df.groupby(group_column)[agg_column].max().reset_index()
            else:
                raise ValueError(f"Invalid aggregation function: {agg_function}")
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error in group by analysis: {str(e)}")
    
    def pivot_table_analysis(self, df, index, columns, values, aggfunc='sum'):
        """
        Create pivot table
        
        Args:
            df: DataFrame to analyze
            index: Column for rows
            columns: Column for columns
            values: Column to aggregate
            aggfunc: Aggregation function
            
        Returns:
            DataFrame: Pivot table results
        """
        try:
            result = pd.pivot_table(
                df,
                index=index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
                fill_value=0
            )
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error creating pivot table: {str(e)}")
    
    def correlation_analysis(self, df, columns=None):
        """
        Calculate correlation matrix
        
        Args:
            df: DataFrame to analyze
            columns: List of columns to include (None = all numeric)
            
        Returns:
            DataFrame: Correlation matrix
        """
        try:
            if columns:
                corr_df = df[columns]
            else:
                corr_df = df.select_dtypes(include=[np.number])
            
            correlation_matrix = corr_df.corr()
            
            return correlation_matrix
            
        except Exception as e:
            raise ValueError(f"Error calculating correlation: {str(e)}")
    
    def descriptive_statistics(self, df, column):
        """
        Calculate descriptive statistics for a column
        
        Args:
            df: DataFrame to analyze
            column: Column name
            
        Returns:
            dict: Statistics dictionary
        """
        try:
            stats_dict = {
                'count': df[column].count(),
                'mean': df[column].mean(),
                'median': df[column].median(),
                'mode': df[column].mode()[0] if len(df[column].mode()) > 0 else None,
                'std': df[column].std(),
                'min': df[column].min(),
                'max': df[column].max(),
                'q25': df[column].quantile(0.25),
                'q75': df[column].quantile(0.75),
                'missing': df[column].isnull().sum(),
                'missing_pct': (df[column].isnull().sum() / len(df)) * 100
            }
            
            return stats_dict
            
        except Exception as e:
            raise ValueError(f"Error calculating statistics: {str(e)}")
    
    def value_counts_analysis(self, df, column, top_n=10):
        """
        Get value counts for a column
        
        Args:
            df: DataFrame to analyze
            column: Column name
            top_n: Number of top values to return
            
        Returns:
            DataFrame: Value counts with percentages
        """
        try:
            counts = df[column].value_counts().head(top_n)
            percentages = (counts / len(df) * 100).round(2)
            
            result = pd.DataFrame({
                'Value': counts.index,
                'Count': counts.values,
                'Percentage': percentages.values
            })
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error in value counts: {str(e)}")
    
    def filter_data(self, df, column, operator, value):
        """
        Filter dataframe based on condition
        
        Args:
            df: DataFrame to filter
            column: Column name
            operator: Comparison operator ('==', '!=', '>', '<', '>=', '<=', 'contains', 'not contains')
            value: Value to compare against
            
        Returns:
            DataFrame: Filtered dataframe
        """
        try:
            if operator == '==':
                result = df[df[column] == value]
            elif operator == '!=':
                result = df[df[column] != value]
            elif operator == '>':
                result = df[df[column] > value]
            elif operator == '<':
                result = df[df[column] < value]
            elif operator == '>=':
                result = df[df[column] >= value]
            elif operator == '<=':
                result = df[df[column] <= value]
            elif operator == 'contains':
                result = df[df[column].astype(str).str.contains(str(value), na=False, case=False)]
            elif operator == 'not contains':
                result = df[~df[column].astype(str).str.contains(str(value), na=False, case=False)]
            else:
                raise ValueError(f"Invalid operator: {operator}")
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error filtering data: {str(e)}")
    
    def sort_data(self, df, columns, ascending=True):
        """
        Sort dataframe by columns
        
        Args:
            df: DataFrame to sort
            columns: Column name or list of column names
            ascending: Sort order (True for ascending, False for descending)
            
        Returns:
            DataFrame: Sorted dataframe
        """
        try:
            if isinstance(columns, str):
                columns = [columns]
            
            result = df.sort_values(by=columns, ascending=ascending)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error sorting data: {str(e)}")
    
    def sql_query(self, df, query):
        """
        Execute SQL query on dataframe
        
        Args:
            df: DataFrame to query
            query: SQL query string
            
        Returns:
            DataFrame: Query results
        """
        try:
            import sqlite3
            
            # Create in-memory SQLite database
            conn = sqlite3.connect(':memory:')
            
            # Load dataframe into SQLite
            df.to_sql('data', conn, index=False, if_exists='replace')
            
            # Execute query
            result = pd.read_sql_query(query, conn)
            
            conn.close()
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error executing SQL query: {str(e)}")
    
    def detect_outliers(self, df, column, method='iqr'):
        """
        Detect outliers in a column
        
        Args:
            df: DataFrame to analyze
            column: Column name
            method: Detection method ('iqr' or 'zscore')
            
        Returns:
            tuple: (outlier_indices, lower_bound, upper_bound)
        """
        try:
            if method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(df[column].dropna()))
                outlier_mask = z_scores > 3
                lower_bound = df[column].mean() - 3 * df[column].std()
                upper_bound = df[column].mean() + 3 * df[column].std()
            
            else:
                raise ValueError(f"Invalid method: {method}")
            
            outlier_indices = df[outlier_mask].index.tolist()
            
            return outlier_indices, lower_bound, upper_bound
            
        except Exception as e:
            raise ValueError(f"Error detecting outliers: {str(e)}")
    
    def calculate_percentage_change(self, df, column, periods=1):
        """
        Calculate percentage change
        
        Args:
            df: DataFrame to analyze
            column: Column name
            periods: Periods to shift for calculating percentage change
            
        Returns:
            Series: Percentage change values
        """
        try:
            pct_change = df[column].pct_change(periods=periods) * 100
            
            return pct_change
            
        except Exception as e:
            raise ValueError(f"Error calculating percentage change: {str(e)}")
    
    def calculate_moving_average(self, df, column, window=3):
        """
        Calculate moving average
        
        Args:
            df: DataFrame to analyze
            column: Column name
            window: Window size for moving average
            
        Returns:
            Series: Moving average values
        """
        try:
            moving_avg = df[column].rolling(window=window).mean()
            
            return moving_avg
            
        except Exception as e:
            raise ValueError(f"Error calculating moving average: {str(e)}")
    
    def calculate_cumulative_sum(self, df, column):
        """
        Calculate cumulative sum
        
        Args:
            df: DataFrame to analyze
            column: Column name
            
        Returns:
            Series: Cumulative sum values
        """
        try:
            cumsum = df[column].cumsum()
            
            return cumsum
            
        except Exception as e:
            raise ValueError(f"Error calculating cumulative sum: {str(e)}")
    
    def rank_data(self, df, column, method='average', ascending=True):
        """
        Rank data in a column
        
        Args:
            df: DataFrame to analyze
            column: Column name
            method: Ranking method ('average', 'min', 'max', 'first', 'dense')
            ascending: Rank order
            
        Returns:
            Series: Rank values
        """
        try:
            ranks = df[column].rank(method=method, ascending=ascending)
            
            return ranks
            
        except Exception as e:
            raise ValueError(f"Error ranking data: {str(e)}")
    
    def categorical_summary(self, df, column):
        """
        Generate summary for categorical column
        
        Args:
            df: DataFrame to analyze
            column: Column name
            
        Returns:
            dict: Summary statistics
        """
        try:
            summary = {
                'unique_count': df[column].nunique(),
                'most_common': df[column].mode()[0] if len(df[column].mode()) > 0 else None,
                'most_common_count': df[column].value_counts().iloc[0] if len(df[column].value_counts()) > 0 else 0,
                'least_common': df[column].value_counts().index[-1] if len(df[column].value_counts()) > 0 else None,
                'missing_count': df[column].isnull().sum(),
                'missing_pct': (df[column].isnull().sum() / len(df)) * 100
            }
            
            return summary
            
        except Exception as e:
            raise ValueError(f"Error in categorical summary: {str(e)}")
