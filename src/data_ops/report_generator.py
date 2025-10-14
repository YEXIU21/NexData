"""
Professional Report Generator
Creates executive reports, presentations, and summaries

SEPARATION OF CONCERNS: Report generation only
"""

import pandas as pd
from datetime import datetime
import os


class ReportGenerator:
    """Generate professional reports for stakeholders"""
    
    @staticmethod
    def generate_executive_summary(df, file_path, analysis_results=None):
        """Generate HTML executive summary report"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Data Analysis Executive Summary</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px;
            background: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 32px;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }}
        .section h2 {{
            color: #2d3748;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            color: #718096;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #2d3748;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f7fafc;
        }}
        .insight {{
            background: #ebf8ff;
            border-left: 4px solid #3182ce;
            padding: 15px;
            margin: 10px 0;
        }}
        .recommendation {{
            background: #f0fff4;
            border-left: 4px solid #38a169;
            padding: 15px;
            margin: 10px 0;
        }}
        .footer {{
            text-align: center;
            color: #718096;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 NexData - Executive Summary</h1>
        <p>Data Analysis Report</p>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="section">
        <h2>Key Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Records</div>
                <div class="metric-value">{len(df):,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Columns</div>
                <div class="metric-value">{len(df.columns)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Data Completeness</div>
                <div class="metric-value">{((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Duplicate Rows</div>
                <div class="metric-value">{df.duplicated().sum():,}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Data Overview</h2>
        <table>
            <tr>
                <th>Column Name</th>
                <th>Data Type</th>
                <th>Non-Null Count</th>
                <th>Unique Values</th>
            </tr>
"""
        
        # Add column information
        for col in df.columns[:20]:  # First 20 columns
            html_content += f"""
            <tr>
                <td><strong>{col}</strong></td>
                <td>{df[col].dtype}</td>
                <td>{df[col].notna().sum():,}</td>
                <td>{df[col].nunique():,}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <div class="section">
        <h2>Statistical Summary</h2>
        <table>
"""
        
        # Add statistical summary for numeric columns
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            stats = numeric_df.describe()
            html_content += "<tr><th>Metric</th>"
            for col in stats.columns[:5]:
                html_content += f"<th>{col}</th>"
            html_content += "</tr>"
            
            for stat in ['mean', 'std', 'min', 'max']:
                html_content += f"<tr><td><strong>{stat.title()}</strong></td>"
                for col in stats.columns[:5]:
                    html_content += f"<td>{stats.loc[stat, col]:.2f}</td>"
                html_content += "</tr>"
        
        html_content += """
        </table>
    </div>
    
    <div class="section">
        <h2>Key Insights</h2>
        <div class="insight">
            <strong>✓ Data Quality:</strong> Dataset contains """ + str(len(df)) + """ records with """ + f"""{((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}% completeness"""
        
        html_content += """
        </div>
"""
        
        if df.duplicated().sum() > 0:
            html_content += f"""
        <div class="insight">
            <strong>⚠ Duplicates Found:</strong> {df.duplicated().sum()} duplicate records identified - consider cleaning
        </div>
"""
        
        # Find columns with high missing rates
        missing_cols = df.columns[df.isnull().sum() / len(df) > 0.2].tolist()
        if missing_cols:
            html_content += f"""
        <div class="insight">
            <strong>⚠ High Missing Data:</strong> Columns with >20% missing: {', '.join(missing_cols[:5])}
        </div>
"""
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <div class="recommendation">
            <strong>→</strong> Review and clean duplicate records to ensure data integrity
        </div>
"""
        
        if missing_cols:
            html_content += """
        <div class="recommendation">
            <strong>→</strong> Address high missing data rates in key columns through imputation or collection
        </div>
"""
        
        html_content += """
        <div class="recommendation">
            <strong>→</strong> Perform additional statistical analysis on key metrics
        </div>
        <div class="recommendation">
            <strong>→</strong> Create visualizations to communicate trends to stakeholders
        </div>
    </div>
    
    <div class="footer">
        <p>This report was generated using <strong>NexData</strong> - Next-Generation Data Analytics</p>
        <p>© 2025 NexData - Confidential</p>
    </div>
</body>
</html>
"""
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return True, file_path
    
    @staticmethod
    def generate_quick_summary_text(df):
        """Generate quick text summary for copy-paste"""
        
        summary = f"""
DATA ANALYSIS SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'=' * 60}

OVERVIEW:
- Total Records: {len(df):,}
- Total Columns: {len(df.columns)}
- Data Completeness: {((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%
- Duplicate Records: {df.duplicated().sum():,}

COLUMNS:
"""
        for col in df.columns[:10]:
            summary += f"- {col} ({df[col].dtype}): {df[col].notna().sum():,} non-null values\n"
        
        if len(df.columns) > 10:
            summary += f"... and {len(df.columns) - 10} more columns\n"
        
        # Numeric summary
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary += f"\nNUMERIC SUMMARY (Top 3 columns):\n"
            for col in numeric_cols[:3]:
                summary += f"\n{col}:\n"
                summary += f"  Mean: {df[col].mean():.2f}\n"
                summary += f"  Median: {df[col].median():.2f}\n"
                summary += f"  Min: {df[col].min():.2f}, Max: {df[col].max():.2f}\n"
        
        summary += f"\nKEY INSIGHTS:\n"
        summary += f"- Dataset quality: {((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.0f}% complete\n"
        
        if df.duplicated().sum() > 0:
            summary += f"- Found {df.duplicated().sum()} duplicate records\n"
        
        missing_cols = df.columns[df.isnull().sum() / len(df) > 0.2].tolist()
        if missing_cols:
            summary += f"- High missing data in: {', '.join(missing_cols[:3])}\n"
        
        summary += "\nRECOMMENDATIONS:\n"
        summary += "- Clean duplicate records for data integrity\n"
        if missing_cols:
            summary += "- Address missing data in key columns\n"
        summary += "- Perform statistical analysis on key metrics\n"
        summary += "- Create visualizations for stakeholder presentation\n"
        
        summary += f"\n{'=' * 60}\n"
        summary += "Report generated by NexData - Next-Generation Data Analytics\n"
        summary += "© 2025 NexData\n"
        
        return summary


class EmailReportFormatter:
    """Format reports for email"""
    
    @staticmethod
    def format_for_email(df, include_data=False):
        """Format data summary for email"""
        
        email_body = f"""
Hello,

Please find below the data analysis summary:

📊 QUICK STATS:
• Total Records: {len(df):,}
• Columns: {len(df.columns)}
• Completeness: {((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%

📈 KEY FINDINGS:
"""
        
        # Top numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            email_body += f"\nTop Metrics:\n"
            for col in numeric_cols[:3]:
                email_body += f"• {col}: Mean={df[col].mean():.2f}, Median={df[col].median():.2f}\n"
        
        if df.duplicated().sum() > 0:
            email_body += f"\n⚠ Note: {df.duplicated().sum()} duplicate records found\n"
        
        email_body += "\n💡 NEXT STEPS:\n"
        email_body += "• Review attached detailed report\n"
        email_body += "• Schedule follow-up meeting for deep dive\n"
        email_body += "• Implement recommended data quality improvements\n"
        
        email_body += f"\n\nGenerated: {datetime.now().strftime('%B %d, %Y')}\n"
        email_body += "\nBest regards,\nData Analysis Team"
        
        return email_body
