"""
Dashboard Templates
Pre-built dashboards for common analytics scenarios

SEPARATION OF CONCERNS: Dashboard template generation only
"""

import pandas as pd
import numpy as np
from datetime import datetime


class DashboardTemplates:
    """Pre-built dashboard templates"""
    
    @staticmethod
    def sales_dashboard(df, date_col, revenue_col, product_col=None, customer_col=None):
        """
        Generate sales dashboard metrics
        
        Parameters:
        -----------
        df : DataFrame
            Sales data
        date_col : str
            Date column
        revenue_col : str
            Revenue column
        product_col : str, optional
            Product column
        customer_col : str, optional
            Customer column
        
        Returns:
        --------
        dashboard : dict
            Dashboard metrics
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            
            dashboard = {}
            
            # Key metrics
            dashboard['total_revenue'] = df_copy[revenue_col].sum()
            dashboard['total_transactions'] = len(df_copy)
            dashboard['avg_transaction_value'] = df_copy[revenue_col].mean()
            dashboard['date_range'] = {
                'start': df_copy[date_col].min(),
                'end': df_copy[date_col].max()
            }
            
            # Time series metrics
            df_copy['date'] = df_copy[date_col].dt.date
            daily_sales = df_copy.groupby('date')[revenue_col].sum().reset_index()
            dashboard['daily_sales'] = daily_sales
            dashboard['best_day'] = {
                'date': daily_sales.loc[daily_sales[revenue_col].idxmax(), 'date'],
                'revenue': daily_sales[revenue_col].max()
            }
            
            # Growth metrics
            df_copy['month'] = df_copy[date_col].dt.to_period('M')
            monthly_sales = df_copy.groupby('month')[revenue_col].sum()
            if len(monthly_sales) >= 2:
                current_month = monthly_sales.iloc[-1]
                previous_month = monthly_sales.iloc[-2]
                dashboard['mom_growth'] = ((current_month - previous_month) / previous_month * 100) if previous_month != 0 else 0
            
            # Product metrics (if available)
            if product_col and product_col in df_copy.columns:
                product_sales = df_copy.groupby(product_col)[revenue_col].sum().sort_values(ascending=False)
                dashboard['top_products'] = product_sales.head(10).to_dict()
            
            # Customer metrics (if available)
            if customer_col and customer_col in df_copy.columns:
                dashboard['unique_customers'] = df_copy[customer_col].nunique()
                dashboard['avg_revenue_per_customer'] = dashboard['total_revenue'] / dashboard['unique_customers']
                
                customer_purchases = df_copy.groupby(customer_col).size()
                dashboard['repeat_customer_rate'] = (customer_purchases > 1).sum() / len(customer_purchases) * 100
            
            return dashboard, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def customer_dashboard(df, customer_col, date_col, revenue_col):
        """
        Generate customer analytics dashboard
        
        Returns:
        --------
        dashboard : dict
            Customer metrics
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            
            dashboard = {}
            
            # Customer acquisition
            first_purchase = df_copy.groupby(customer_col)[date_col].min()
            dashboard['total_customers'] = len(first_purchase)
            
            # Cohort by month
            first_purchase_month = first_purchase.dt.to_period('M')
            cohort_counts = first_purchase_month.value_counts().sort_index()
            dashboard['new_customers_by_month'] = cohort_counts.to_dict()
            
            # Customer lifetime metrics
            customer_metrics = df_copy.groupby(customer_col).agg({
                revenue_col: 'sum',
                date_col: 'count'
            })
            customer_metrics.columns = ['lifetime_value', 'purchase_count']
            
            dashboard['avg_customer_ltv'] = customer_metrics['lifetime_value'].mean()
            dashboard['avg_purchases_per_customer'] = customer_metrics['purchase_count'].mean()
            
            # Customer segmentation by value
            dashboard['top_10_pct_customers_revenue'] = (
                customer_metrics.nlargest(int(len(customer_metrics) * 0.1), 'lifetime_value')['lifetime_value'].sum() /
                customer_metrics['lifetime_value'].sum() * 100
            )
            
            # Active vs inactive customers (last 90 days)
            max_date = df_copy[date_col].max()
            recent_customers = df_copy[df_copy[date_col] >= max_date - pd.Timedelta(days=90)][customer_col].unique()
            dashboard['active_customers_90d'] = len(recent_customers)
            dashboard['active_rate'] = len(recent_customers) / dashboard['total_customers'] * 100
            
            return dashboard, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def product_dashboard(df, product_col, revenue_col, quantity_col=None):
        """
        Generate product performance dashboard
        
        Returns:
        --------
        dashboard : dict
            Product metrics
        """
        try:
            dashboard = {}
            
            # Product performance
            product_metrics = df.groupby(product_col).agg({
                revenue_col: ['sum', 'mean', 'count']
            })
            product_metrics.columns = ['total_revenue', 'avg_price', 'units_sold']
            product_metrics = product_metrics.sort_values('total_revenue', ascending=False)
            
            dashboard['total_products'] = len(product_metrics)
            dashboard['top_products_by_revenue'] = product_metrics.head(10)[['total_revenue', 'units_sold']].to_dict()
            
            # Product concentration
            total_revenue = product_metrics['total_revenue'].sum()
            dashboard['top_20_pct_products_revenue'] = (
                product_metrics.head(int(len(product_metrics) * 0.2))['total_revenue'].sum() /
                total_revenue * 100
            )
            
            # Average metrics
            dashboard['avg_product_revenue'] = product_metrics['total_revenue'].mean()
            dashboard['avg_units_per_product'] = product_metrics['units_sold'].mean()
            
            # Quantity analysis (if available)
            if quantity_col and quantity_col in df.columns:
                dashboard['total_units_sold'] = df[quantity_col].sum()
                dashboard['avg_quantity_per_transaction'] = df[quantity_col].mean()
            
            return dashboard, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def format_dashboard_report(dashboard, dashboard_type='sales'):
        """
        Format dashboard metrics as readable report
        
        Parameters:
        -----------
        dashboard : dict
            Dashboard metrics
        dashboard_type : str
            Type of dashboard ('sales', 'customer', 'product')
        
        Returns:
        --------
        report : str
            Formatted report text
        """
        report = f"\n{'='*60}\n"
        report += f"{dashboard_type.upper()} DASHBOARD\n"
        report += f"{'='*60}\n\n"
        
        for key, value in dashboard.items():
            if isinstance(value, dict):
                report += f"\n{key.replace('_', ' ').title()}:\n"
                for sub_key, sub_value in value.items():
                    report += f"  • {sub_key}: {sub_value}\n"
            elif isinstance(value, (int, float)):
                if 'revenue' in key.lower() or 'value' in key.lower():
                    report += f"• {key.replace('_', ' ').title()}: ${value:,.2f}\n"
                elif 'rate' in key.lower() or 'pct' in key.lower() or 'percent' in key.lower():
                    report += f"• {key.replace('_', ' ').title()}: {value:.2f}%\n"
                else:
                    report += f"• {key.replace('_', ' ').title()}: {value:,.0f}\n"
            else:
                report += f"• {key.replace('_', ' ').title()}: {value}\n"
        
        report += f"\n{'='*60}\n"
        return report
