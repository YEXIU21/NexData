"""
AI Service
Handles AI-powered features like Data Quality Advisor and Report Generation
Extracted from main_window.py to improve code organization
"""

import pandas as pd
import numpy as np
from datetime import datetime


class AIService:
    """Service class for AI-powered data analysis features"""
    
    def __init__(self):
        pass
    
    def analyze_data_quality(self, df):
        """
        Analyze dataset and return list of recommendations
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            list: List of recommendation dictionaries
        """
        recommendations = []
        
        # 1. Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            recommendations.append({
                'priority': 'High',
                'issue': f'Found {duplicates} duplicate row(s)',
                'impact': 'Duplicate data can skew analysis results',
                'tool': 'Remove Duplicates'
            })
        
        # 2. Check for missing values
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            total_missing = df.isnull().sum().sum()
            # Check if smart fill is possible
            id_cols = [c for c in df.columns if 'id' in c.lower()]
            
            if id_cols and missing_cols:
                recommendations.append({
                    'priority': 'High',
                    'issue': f'Missing values in {len(missing_cols)} column(s) ({total_missing} total)',
                    'impact': 'Can be filled using Smart Fill by matching IDs',
                    'tool': 'Smart Fill Missing Data'
                })
            else:
                recommendations.append({
                    'priority': 'Medium',
                    'issue': f'Missing values in {len(missing_cols)} column(s) ({total_missing} total)',
                    'impact': 'Missing data can affect analysis completeness',
                    'tool': 'Handle Missing Values'
                })
        
        # 3. Check for whitespace issues
        text_cols = df.select_dtypes(include=['object']).columns
        whitespace_issues = 0
        for col in text_cols:
            has_issues = (df[col].astype(str) != df[col].astype(str).str.strip()).any()
            has_double_space = df[col].astype(str).str.contains(r'\s{2,}', na=False).any()
            if has_issues or has_double_space:
                whitespace_issues += 1
        
        if whitespace_issues > 0:
            recommendations.append({
                'priority': 'Medium',
                'issue': f'Whitespace issues in {whitespace_issues} column(s)',
                'impact': 'Extra spaces can cause matching and sorting problems',
                'tool': 'Trim All Columns'
            })
        
        # 4. Check for mixed case in text columns
        mixed_case_cols = []
        for col in text_cols[:5]:  # Check first 5 text columns
            sample = df[col].dropna().head(10)
            if len(sample) > 0:
                has_upper = sample.astype(str).str.isupper().any()
                has_lower = sample.astype(str).str.islower().any()
                has_title = sample.astype(str).str.istitle().any()
                if sum([has_upper, has_lower, has_title]) > 1:
                    mixed_case_cols.append(col)
        
        if mixed_case_cols:
            recommendations.append({
                'priority': 'Low',
                'issue': f'Inconsistent text case in {len(mixed_case_cols)} column(s)',
                'impact': 'Mixed case affects sorting and grouping consistency',
                'tool': 'Standardize Text Case'
            })
        
        # 5. Check for empty rows/columns
        empty_rows = df.isnull().all(axis=1).sum()
        empty_cols = df.isnull().all(axis=0).sum()
        if empty_rows > 0 or empty_cols > 0:
            recommendations.append({
                'priority': 'High',
                'issue': f'Found {empty_rows} empty row(s) and {empty_cols} empty column(s)',
                'impact': 'Empty data wastes storage and processing time',
                'tool': 'Remove Empty Rows/Columns'
            })
        
        # 6. Check for outliers in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_cols = []
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > 0:
                outlier_cols.append((col, outliers))
        
        if outlier_cols:
            total_outliers = sum(count for _, count in outlier_cols)
            recommendations.append({
                'priority': 'Medium',
                'issue': f'Potential outliers in {len(outlier_cols)} numeric column(s) ({total_outliers} values)',
                'impact': 'Outliers can skew statistical analysis',
                'tool': 'Remove Outliers'
            })
        
        return recommendations
    
    def generate_report(self, df):
        """
        Generate comprehensive AI analysis report
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            str: Formatted report text
        """
        report = []
        report.append("=" * 80)
        report.append("                    DATA ANALYSIS REPORT")
        report.append("                  Generated by NexData AI")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Dataset: {len(df)} rows × {len(df.columns)} columns\n")
        
        # EXECUTIVE SUMMARY
        report.append("\n" + "=" * 80)
        report.append("EXECUTIVE SUMMARY")
        report.append("=" * 80)
        
        # Key metrics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            total_value_col = [col for col in numeric_cols if 'total' in col.lower() or 'amount' in col.lower() or 'revenue' in col.lower() or 'sales' in col.lower()]
            if total_value_col:
                total_sum = df[total_value_col[0]].sum()
                total_avg = df[total_value_col[0]].mean()
                report.append(f"\n• Total Value: ${total_sum:,.2f}")
                report.append(f"• Average Value: ${total_avg:,.2f}")
        
        # Data quality score
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        duplicates = df.duplicated().sum()
        quality_score = max(0, 100 - missing_pct - (duplicates / len(df) * 10))
        report.append(f"• Data Quality Score: {quality_score:.1f}/100")
        report.append(f"• Completeness: {100 - missing_pct:.1f}%")
        report.append(f"• Duplicates: {duplicates} rows")
        
        # KEY FINDINGS
        report.append("\n" + "=" * 80)
        report.append("KEY FINDINGS")
        report.append("=" * 80)
        
        findings = self._generate_key_findings(df)
        for idx, finding in enumerate(findings, 1):
            report.append(f"\n{idx}. {finding}")
        
        # DETAILED STATISTICS
        report.append("\n\n" + "=" * 80)
        report.append("DETAILED STATISTICS")
        report.append("=" * 80)
        
        # Numeric columns
        if len(numeric_cols) > 0:
            report.append("\nNumeric Columns Analysis:")
            for col in numeric_cols[:5]:  # Top 5 numeric columns
                report.append(f"\n  {col}:")
                report.append(f"    - Mean: {df[col].mean():.2f}")
                report.append(f"    - Median: {df[col].median():.2f}")
                report.append(f"    - Std Dev: {df[col].std():.2f}")
                report.append(f"    - Min: {df[col].min():.2f}")
                report.append(f"    - Max: {df[col].max():.2f}")
        
        # Categorical columns
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            report.append("\n\nCategorical Columns Analysis:")
            for col in cat_cols[:5]:  # Top 5 categorical columns
                unique_count = df[col].nunique()
                most_common = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
                report.append(f"\n  {col}:")
                report.append(f"    - Unique values: {unique_count}")
                report.append(f"    - Most common: {most_common}")
                if unique_count <= 10:
                    value_counts = df[col].value_counts().head(5)
                    report.append(f"    - Top values:")
                    for val, count in value_counts.items():
                        report.append(f"        • {val}: {count} ({count/len(df)*100:.1f}%)")
        
        # DATA QUALITY ISSUES
        report.append("\n\n" + "=" * 80)
        report.append("DATA QUALITY ASSESSMENT")
        report.append("=" * 80)
        
        issues_found = []
        if duplicates > 0:
            issues_found.append(f"⚠️  {duplicates} duplicate rows detected")
        
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            total_missing = df.isnull().sum().sum()
            issues_found.append(f"⚠️  Missing values in {len(missing_cols)} columns ({total_missing} total)")
        
        if not issues_found:
            report.append("\n✅ No significant data quality issues detected!")
        else:
            report.append("\nIssues Detected:")
            for issue in issues_found:
                report.append(f"  {issue}")
        
        # RECOMMENDATIONS
        report.append("\n\n" + "=" * 80)
        report.append("AI RECOMMENDATIONS")
        report.append("=" * 80)
        
        recommendations = self._generate_recommendations(df)
        for idx, rec in enumerate(recommendations, 1):
            report.append(f"\n{idx}. {rec}")
        
        # NEXT STEPS
        report.append("\n\n" + "=" * 80)
        report.append("SUGGESTED NEXT STEPS")
        report.append("=" * 80)
        report.append("\n1. Clean data using recommended tools from Data Quality Advisor")
        report.append("2. Perform deeper analysis on key metrics identified above")
        report.append("3. Create visualizations to communicate findings")
        report.append("4. Export cleaned data for further processing")
        report.append("5. Set up regular monitoring of key indicators")
        
        # Footer
        report.append("\n\n" + "=" * 80)
        report.append("End of Report")
        report.append("=" * 80)
        report.append("\nGenerated by NexData AI - Professional Data Analysis Tool")
        
        return "\n".join(report)
    
    def _generate_key_findings(self, df):
        """Generate key insights from data"""
        findings = []
        
        # Finding 1: Dataset size insight
        row_count = len(df)
        col_count = len(df.columns)
        findings.append(f"Dataset contains {row_count:,} records across {col_count} dimensions, providing substantial data for analysis.")
        
        # Finding 2: Value concentration
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            for col in numeric_cols:
                if 'total' in col.lower() or 'amount' in col.lower() or 'price' in col.lower():
                    max_val = df[col].max()
                    avg_val = df[col].mean()
                    if max_val > avg_val * 2:
                        findings.append(f"Top {col} value (${max_val:,.2f}) is {max_val/avg_val:.1f}x higher than average, indicating significant variation.")
                    break
        
        # Finding 3: Categorical distribution
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df[col].nunique() < 20:
                mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else None
                if mode_val:
                    mode_pct = (df[col] == mode_val).sum() / len(df) * 100
                    if mode_pct > 30:
                        findings.append(f"'{mode_val}' dominates {col} category with {mode_pct:.1f}% of records.")
                break
        
        # Finding 4: Data completeness
        complete_rows = len(df.dropna())
        complete_pct = complete_rows / len(df) * 100
        if complete_pct > 95:
            findings.append(f"Dataset is {complete_pct:.1f}% complete with minimal missing values, ensuring reliable analysis.")
        elif complete_pct < 80:
            findings.append(f"Only {complete_pct:.1f}% of rows are complete. Missing data should be addressed before analysis.")
        
        return findings[:5]  # Return top 5 findings
    
    def _generate_recommendations(self, df):
        """Generate actionable recommendations"""
        recs = []
        
        # Based on data quality
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            recs.append("Remove duplicate records to ensure accuracy in aggregations and counts.")
        
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            recs.append(f"Address missing values in {len(missing_cols)} columns using Smart Fill or imputation methods.")
        
        # Based on data types
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 2:
            recs.append("Perform correlation analysis to identify relationships between numeric variables.")
        
        # Based on categorical data
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            recs.append("Create group-by analysis to segment data by categorical variables and identify patterns.")
        
        # Visualization
        if len(numeric_cols) > 0 and len(cat_cols) > 0:
            recs.append("Generate visualizations to communicate key trends and distributions effectively.")
        
        return recs[:5]  # Return top 5 recommendations
