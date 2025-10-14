"""
Data Quality Checker
Automated data validation and quality assessment

SEPARATION OF CONCERNS: Data quality validation only
"""

import pandas as pd
import numpy as np
from datetime import datetime


class DataQualityChecker:
    """Comprehensive data quality assessment"""
    
    @staticmethod
    def assess_quality(df):
        """
        Perform comprehensive data quality assessment
        
        Parameters:
        -----------
        df : DataFrame
            Data to assess
        
        Returns:
        --------
        quality_report : dict
            Quality assessment results
        """
        report = {
            'overall_score': 0,
            'completeness': {},
            'consistency': {},
            'validity': {},
            'uniqueness': {},
            'timeliness': {},
            'issues': [],
            'recommendations': []
        }
        
        # 1. Completeness Check
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        completeness_score = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
        
        report['completeness'] = {
            'score': completeness_score,
            'total_cells': total_cells,
            'missing_cells': missing_cells,
            'missing_percentage': (missing_cells / total_cells * 100) if total_cells > 0 else 0
        }
        
        # Column-wise completeness
        missing_by_column = df.isnull().sum()
        critical_missing = missing_by_column[missing_by_column > len(df) * 0.3]
        if len(critical_missing) > 0:
            report['issues'].append(f"⚠️ {len(critical_missing)} columns have >30% missing data")
            report['recommendations'].append(f"Review columns: {', '.join(critical_missing.index.tolist())}")
        
        # 2. Uniqueness Check
        duplicate_rows = df.duplicated().sum()
        uniqueness_score = ((len(df) - duplicate_rows) / len(df) * 100) if len(df) > 0 else 0
        
        report['uniqueness'] = {
            'score': uniqueness_score,
            'total_rows': len(df),
            'duplicate_rows': duplicate_rows,
            'duplicate_percentage': (duplicate_rows / len(df) * 100) if len(df) > 0 else 0
        }
        
        if duplicate_rows > 0:
            report['issues'].append(f"⚠️ Found {duplicate_rows} duplicate rows")
            report['recommendations'].append("Consider removing duplicates for data integrity")
        
        # 3. Consistency Check
        consistency_issues = []
        
        # Check for mixed data types in object columns
        for col in df.select_dtypes(include=['object']).columns:
            try:
                # Try to identify if column should be numeric
                numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if numeric_count > len(df) * 0.5:
                    consistency_issues.append(f"Column '{col}' appears to be numeric but stored as text")
            except:
                pass
        
        # Check date columns
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(df[col], errors='raise')
                except:
                    consistency_issues.append(f"Column '{col}' may contain invalid dates")
        
        consistency_score = 100 - (len(consistency_issues) * 10)
        consistency_score = max(0, consistency_score)
        
        report['consistency'] = {
            'score': consistency_score,
            'issues_found': len(consistency_issues),
            'details': consistency_issues
        }
        
        # 4. Validity Check (range and format checks)
        validity_issues = []
        
        # Check for negative values in likely-positive columns
        for col in df.select_dtypes(include=[np.number]).columns:
            if any(keyword in col.lower() for keyword in ['price', 'amount', 'revenue', 'quantity', 'count']):
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    validity_issues.append(f"Column '{col}' has {negative_count} negative values")
        
        # Check for outliers using IQR method
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 3 * IQR)) | (df[col] > (Q3 + 3 * IQR))).sum()
            if outliers > len(df) * 0.05:  # More than 5% outliers
                validity_issues.append(f"Column '{col}' has {outliers} potential outliers")
        
        validity_score = 100 - (len(validity_issues) * 5)
        validity_score = max(0, validity_score)
        
        report['validity'] = {
            'score': validity_score,
            'issues_found': len(validity_issues),
            'details': validity_issues
        }
        
        # 5. Overall Quality Score
        report['overall_score'] = round(
            (completeness_score * 0.3 +
             uniqueness_score * 0.2 +
             consistency_score * 0.25 +
             validity_score * 0.25), 2
        )
        
        # Add overall issues to report
        if report['overall_score'] >= 90:
            report['quality_level'] = 'Excellent'
        elif report['overall_score'] >= 75:
            report['quality_level'] = 'Good'
        elif report['overall_score'] >= 60:
            report['quality_level'] = 'Fair'
        else:
            report['quality_level'] = 'Poor'
        
        return report
    
    @staticmethod
    def validate_column_types(df):
        """
        Validate and suggest correct data types
        
        Returns:
        --------
        suggestions : dict
            Column type suggestions
        """
        suggestions = {}
        
        for col in df.columns:
            current_type = str(df[col].dtype)
            suggested_type = None
            
            # Check if object column should be numeric
            if current_type == 'object':
                try:
                    numeric_converted = pd.to_numeric(df[col], errors='coerce')
                    if numeric_converted.notna().sum() > len(df) * 0.8:
                        suggested_type = 'numeric'
                except:
                    pass
                
                # Check if should be datetime
                try:
                    date_converted = pd.to_datetime(df[col], errors='coerce')
                    if date_converted.notna().sum() > len(df) * 0.8:
                        suggested_type = 'datetime'
                except:
                    pass
                
                # Check if should be category
                if df[col].nunique() < len(df) * 0.05:
                    suggested_type = 'category'
            
            if suggested_type:
                suggestions[col] = {
                    'current': current_type,
                    'suggested': suggested_type
                }
        
        return suggestions
    
    @staticmethod
    def check_data_patterns(df):
        """
        Check for common data patterns and issues
        
        Returns:
        --------
        patterns : dict
            Detected patterns
        """
        patterns = {
            'all_null_columns': [],
            'constant_columns': [],
            'high_cardinality_columns': [],
            'potential_id_columns': []
        }
        
        for col in df.columns:
            # All null
            if df[col].isnull().all():
                patterns['all_null_columns'].append(col)
            
            # Constant value
            elif df[col].nunique() == 1:
                patterns['constant_columns'].append(col)
            
            # High cardinality (unique values > 50% of rows)
            elif df[col].nunique() > len(df) * 0.5:
                patterns['high_cardinality_columns'].append(col)
            
            # Potential ID column (all unique)
            if df[col].nunique() == len(df):
                patterns['potential_id_columns'].append(col)
        
        return patterns
    
    @staticmethod
    def generate_quality_report_text(quality_report):
        """
        Generate human-readable quality report
        
        Parameters:
        -----------
        quality_report : dict
            Quality assessment results
        
        Returns:
        --------
        report_text : str
            Formatted report
        """
        report = f"\n{'='*60}\n"
        report += "DATA QUALITY ASSESSMENT REPORT\n"
        report += f"{'='*60}\n\n"
        
        report += f"Overall Quality Score: {quality_report['overall_score']:.2f}/100\n"
        report += f"Quality Level: {quality_report['quality_level']}\n\n"
        
        report += "--- DETAILED SCORES ---\n"
        report += f"Completeness: {quality_report['completeness']['score']:.2f}%\n"
        report += f"  Missing Cells: {quality_report['completeness']['missing_cells']:,} ({quality_report['completeness']['missing_percentage']:.2f}%)\n\n"
        
        report += f"Uniqueness: {quality_report['uniqueness']['score']:.2f}%\n"
        report += f"  Duplicate Rows: {quality_report['uniqueness']['duplicate_rows']:,}\n\n"
        
        report += f"Consistency: {quality_report['consistency']['score']:.2f}%\n"
        if quality_report['consistency']['details']:
            for issue in quality_report['consistency']['details']:
                report += f"  • {issue}\n"
        
        report += f"\nValidity: {quality_report['validity']['score']:.2f}%\n"
        if quality_report['validity']['details']:
            for issue in quality_report['validity']['details'][:5]:  # Top 5 issues
                report += f"  • {issue}\n"
        
        if quality_report['issues']:
            report += "\n--- KEY ISSUES ---\n"
            for issue in quality_report['issues']:
                report += f"{issue}\n"
        
        if quality_report['recommendations']:
            report += "\n--- RECOMMENDATIONS ---\n"
            for rec in quality_report['recommendations']:
                report += f"✓ {rec}\n"
        
        report += f"\n{'='*60}\n"
        
        return report
