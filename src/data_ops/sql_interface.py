"""
SQL Query Interface
Execute SQL-like queries on pandas DataFrames

SEPARATION OF CONCERNS: SQL query execution only
"""

import pandas as pd
import sqlite3
import io


class SQLInterface:
    """SQL query interface for DataFrames"""
    
    @staticmethod
    def execute_query(df, query):
        """Execute SQL query on DataFrame"""
        try:
            # Create in-memory SQLite database
            conn = sqlite3.connect(':memory:')
            
            # Write DataFrame to SQL
            df.to_sql('data', conn, index=False, if_exists='replace')
            
            # Execute query
            result = pd.read_sql_query(query, conn)
            
            conn.close()
            
            return result, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def validate_query(query):
        """Validate SQL query syntax"""
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE TABLE', 'INSERT', 'UPDATE']
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False, f"Dangerous operation '{keyword}' not allowed for safety"
        
        return True, "Query is safe"
    
    @staticmethod
    def get_example_queries():
        """Return example SQL queries"""
        examples = {
            'Basic SELECT': 'SELECT * FROM data LIMIT 10',
            'Filter rows': 'SELECT * FROM data WHERE column_name > 100',
            'Aggregate': 'SELECT category, COUNT(*), AVG(value) FROM data GROUP BY category',
            'Join (self)': 'SELECT a.*, b.column FROM data a INNER JOIN data b ON a.id = b.id',
            'Order by': 'SELECT * FROM data ORDER BY column_name DESC',
            'Multiple conditions': 'SELECT * FROM data WHERE col1 > 50 AND col2 = "value"',
            'Top N': 'SELECT * FROM data ORDER BY sales DESC LIMIT 5',
            'Distinct': 'SELECT DISTINCT category FROM data',
            'Group with HAVING': 'SELECT category, COUNT(*) as cnt FROM data GROUP BY category HAVING cnt > 10',
            'Date filter': 'SELECT * FROM data WHERE date_column >= "2024-01-01"'
        }
        return examples


class DataProfiler:
    """Generate comprehensive data profiling reports"""
    
    @staticmethod
    def generate_profile(df):
        """Generate comprehensive data profile"""
        profile = {
            'overview': DataProfiler._overview(df),
            'columns': DataProfiler._column_profiles(df),
            'correlations': DataProfiler._correlation_insights(df),
            'quality': DataProfiler._data_quality(df),
            'recommendations': DataProfiler._recommendations(df)
        }
        return profile
    
    @staticmethod
    def _overview(df):
        """Dataset overview"""
        return {
            'n_rows': len(df),
            'n_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'duplicate_rows': df.duplicated().sum(),
            'total_missing': df.isnull().sum().sum(),
            'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        }
    
    @staticmethod
    def _column_profiles(df):
        """Profile each column"""
        profiles = {}
        
        for col in df.columns:
            profile = {
                'dtype': str(df[col].dtype),
                'missing_count': df[col].isnull().sum(),
                'missing_percentage': (df[col].isnull().sum() / len(df)) * 100,
                'unique_count': df[col].nunique(),
                'unique_percentage': (df[col].nunique() / len(df)) * 100
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                profile.update({
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'q25': df[col].quantile(0.25),
                    'q75': df[col].quantile(0.75),
                    'skewness': df[col].skew(),
                    'kurtosis': df[col].kurtosis(),
                    'zeros_count': (df[col] == 0).sum()
                })
            elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object':
                value_counts = df[col].value_counts()
                profile.update({
                    'most_common': value_counts.index[0] if len(value_counts) > 0 else None,
                    'most_common_freq': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                    'least_common': value_counts.index[-1] if len(value_counts) > 0 else None
                })
            
            profiles[col] = profile
        
        return profiles
    
    @staticmethod
    def _correlation_insights(df):
        """Find correlation insights"""
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return {'message': 'Not enough numeric columns for correlation analysis'}
        
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corr.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': corr_val,
                        'strength': 'Strong positive' if corr_val > 0 else 'Strong negative'
                    })
        
        return {
            'strong_correlations': strong_corr,
            'correlation_matrix_shape': corr_matrix.shape
        }
    
    @staticmethod
    def _data_quality(df):
        """Assess data quality"""
        issues = []
        
        # Check for high missing data
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 50:
                issues.append({
                    'type': 'High Missing Data',
                    'column': col,
                    'percentage': missing_pct,
                    'severity': 'Critical'
                })
            elif missing_pct > 20:
                issues.append({
                    'type': 'Moderate Missing Data',
                    'column': col,
                    'percentage': missing_pct,
                    'severity': 'Warning'
                })
        
        # Check for low variance
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if df[col].std() == 0:
                issues.append({
                    'type': 'Zero Variance',
                    'column': col,
                    'severity': 'Warning',
                    'message': 'Column has no variation (all values are the same)'
                })
        
        # Check for high cardinality in categorical
        for col in df.select_dtypes(include=['object']).columns:
            unique_pct = (df[col].nunique() / len(df)) * 100
            if unique_pct > 90:
                issues.append({
                    'type': 'High Cardinality',
                    'column': col,
                    'unique_percentage': unique_pct,
                    'severity': 'Info',
                    'message': 'Might be a unique identifier rather than categorical'
                })
        
        return {
            'total_issues': len(issues),
            'issues': issues,
            'quality_score': max(0, 100 - (len(issues) * 5))  # Simple quality score
        }
    
    @staticmethod
    def _recommendations(df):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check duplicates
        if df.duplicated().sum() > 0:
            recommendations.append({
                'action': 'Remove Duplicates',
                'reason': f'Found {df.duplicated().sum()} duplicate rows',
                'priority': 'High'
            })
        
        # Check missing data
        missing_cols = df.columns[df.isnull().any()].tolist()
        if len(missing_cols) > 0:
            recommendations.append({
                'action': 'Handle Missing Values',
                'reason': f'{len(missing_cols)} columns have missing data',
                'priority': 'High',
                'affected_columns': missing_cols[:5]  # Show first 5
            })
        
        # Check for normalization
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            scales_vary = df[numeric_cols].std().max() / (df[numeric_cols].std().min() + 1e-10) > 100
            if scales_vary:
                recommendations.append({
                    'action': 'Normalize Data',
                    'reason': 'Numeric columns have vastly different scales',
                    'priority': 'Medium'
                })
        
        # Check datetime conversion
        for col in df.select_dtypes(include=['object']).columns[:10]:  # Check first 10 object columns
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(df[col].head(10), errors='raise')
                    recommendations.append({
                        'action': 'Convert to DateTime',
                        'reason': f'Column "{col}" appears to contain dates',
                        'priority': 'Medium',
                        'column': col
                    })
                    break  # Only suggest once
                except:
                    pass
        
        return recommendations
