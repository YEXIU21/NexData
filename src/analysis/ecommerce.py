"""
E-commerce/Shopify Specific Analysis
Business metrics and KPIs for e-commerce data

SEPARATION OF CONCERNS: Only e-commerce business logic
"""

import pandas as pd
import numpy as np


class EcommerceAnalyzer:
    """E-commerce specific analysis functions"""
    
    @staticmethod
    def identify_revenue_columns(df):
        """Auto-detect revenue/sales related columns"""
        keywords = ['revenue', 'sales', 'price', 'amount', 'total', 'value']
        revenue_cols = [col for col in df.columns 
                       if any(keyword in col.lower() for keyword in keywords)]
        return revenue_cols
    
    @staticmethod
    def identify_customer_columns(df):
        """Auto-detect customer related columns"""
        keywords = ['customer', 'user', 'buyer', 'client']
        customer_cols = [col for col in df.columns 
                        if any(keyword in col.lower() for keyword in keywords)]
        return customer_cols
    
    @staticmethod
    def calculate_revenue_metrics(df, revenue_column):
        """Calculate key revenue metrics"""
        metrics = {
            'total_revenue': df[revenue_column].sum(),
            'average_order_value': df[revenue_column].mean(),
            'median_order_value': df[revenue_column].median(),
            'max_order_value': df[revenue_column].max(),
            'min_order_value': df[revenue_column].min(),
            'std_order_value': df[revenue_column].std()
        }
        return metrics
    
    @staticmethod
    def calculate_customer_metrics(df, customer_column):
        """Calculate customer metrics"""
        metrics = {
            'total_customers': df[customer_column].nunique(),
            'total_orders': len(df),
            'orders_per_customer': len(df) / df[customer_column].nunique()
        }
        return metrics
    
    @staticmethod
    def top_products(df, product_column, metric_column='quantity', top_n=10):
        """Get top products by a metric"""
        if product_column not in df.columns:
            return None
        
        top = df.groupby(product_column)[metric_column].sum().sort_values(ascending=False).head(top_n)
        return top
    
    @staticmethod
    def customer_segmentation_simple(df, customer_column, revenue_column):
        """Simple customer segmentation by total spending"""
        customer_spending = df.groupby(customer_column)[revenue_column].sum()
        
        # Define segments
        q25, q75 = customer_spending.quantile([0.25, 0.75])
        
        def segment(value):
            if value < q25:
                return 'Low Value'
            elif value < q75:
                return 'Medium Value'
            else:
                return 'High Value'
        
        customer_segments = customer_spending.apply(segment)
        segment_counts = customer_segments.value_counts()
        
        return segment_counts
    
    @staticmethod
    def sales_by_category(df, category_column, revenue_column):
        """Analyze sales by category"""
        if category_column not in df.columns:
            return None
        
        category_sales = df.groupby(category_column)[revenue_column].agg([
            ('total_sales', 'sum'),
            ('avg_sales', 'mean'),
            ('order_count', 'count')
        ]).sort_values('total_sales', ascending=False)
        
        return category_sales
    
    @staticmethod
    def conversion_funnel(df, stages):
        """Calculate conversion funnel metrics"""
        funnel = {}
        for i, stage in enumerate(stages):
            count = df[stage].sum() if stage in df.columns else 0
            funnel[stage] = {
                'count': count,
                'percentage': 100.0 if i == 0 else (count / funnel[stages[0]]['count'] * 100)
            }
        return funnel
    
    @staticmethod
    def cohort_analysis(df, customer_column, date_column, revenue_column):
        """Basic cohort analysis"""
        # Convert to datetime
        df_cohort = df.copy()
        df_cohort[date_column] = pd.to_datetime(df_cohort[date_column])
        
        # Get first purchase date per customer
        df_cohort['cohort_month'] = df_cohort.groupby(customer_column)[date_column].transform('min').dt.to_period('M')
        df_cohort['order_month'] = df_cohort[date_column].dt.to_period('M')
        
        # Calculate cohort index
        def get_period_diff(row):
            return (row['order_month'] - row['cohort_month']).n
        
        df_cohort['cohort_index'] = df_cohort.apply(get_period_diff, axis=1)
        
        # Pivot table
        cohort_data = df_cohort.groupby(['cohort_month', 'cohort_index'])[customer_column].nunique()
        cohort_pivot = cohort_data.unstack(fill_value=0)
        
        return cohort_pivot


class ShopifyMetrics:
    """Shopify specific metrics"""
    
    @staticmethod
    def calculate_aov(df, revenue_column):
        """Calculate Average Order Value"""
        return df[revenue_column].mean()
    
    @staticmethod
    def calculate_ltv_simple(df, customer_column, revenue_column):
        """Simple Customer Lifetime Value calculation"""
        customer_total = df.groupby(customer_column)[revenue_column].sum()
        return customer_total.mean()
    
    @staticmethod
    def product_performance(df, product_column, revenue_column, quantity_column):
        """Analyze product performance"""
        performance = df.groupby(product_column).agg({
            revenue_column: ['sum', 'mean'],
            quantity_column: 'sum'
        })
        performance.columns = ['total_revenue', 'avg_revenue', 'total_quantity']
        performance['revenue_per_unit'] = performance['total_revenue'] / performance['total_quantity']
        return performance.sort_values('total_revenue', ascending=False)
