"""
RFM Customer Segmentation
Recency, Frequency, Monetary Analysis for Customer Segmentation

SEPARATION OF CONCERNS: Customer segmentation analysis only
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class RFMSegmentation:
    """RFM Analysis for Customer Segmentation"""
    
    @staticmethod
    def calculate_rfm(df, customer_col, date_col, revenue_col, reference_date=None):
        """
        Calculate RFM scores
        
        Parameters:
        -----------
        df : DataFrame
            Transaction data
        customer_col : str
            Column with customer ID
        date_col : str
            Column with transaction date
        revenue_col : str
            Column with revenue/amount
        reference_date : datetime, optional
            Reference date for recency calculation (default: max date in data)
        
        Returns:
        --------
        rfm_df : DataFrame
            RFM scores for each customer
        """
        try:
            # Convert date column
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            
            # Set reference date
            if reference_date is None:
                reference_date = df_copy[date_col].max()
            
            # Calculate RFM metrics
            rfm = df_copy.groupby(customer_col).agg({
                date_col: lambda x: (reference_date - x.max()).days,  # Recency
                customer_col: 'count',                                  # Frequency
                revenue_col: 'sum'                                      # Monetary
            })
            
            rfm.columns = ['Recency', 'Frequency', 'Monetary']
            
            # Calculate RFM scores (1-5, where 5 is best)
            rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
            rfm['F_Score'] = pd.qcut(rfm['Frequency'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
            rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
            
            # Convert to int
            rfm['R_Score'] = rfm['R_Score'].astype(int)
            rfm['F_Score'] = rfm['F_Score'].astype(int)
            rfm['M_Score'] = rfm['M_Score'].astype(int)
            
            # Calculate total RFM score
            rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
            
            # Assign segments
            rfm['Segment'] = rfm.apply(RFMSegmentation._assign_segment, axis=1)
            
            return rfm.reset_index(), None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def _assign_segment(row):
        """Assign customer segment based on RFM scores"""
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        
        # Champions: Recent, frequent, high spenders
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        
        # Loyal Customers: Frequent, good spenders
        elif f >= 4 and m >= 3:
            return 'Loyal Customers'
        
        # Potential Loyalists: Recent, decent frequency
        elif r >= 3 and f >= 3:
            return 'Potential Loyalists'
        
        # New Customers: Recent, low frequency
        elif r >= 4 and f <= 2:
            return 'New Customers'
        
        # Promising: Recent, moderate spenders
        elif r >= 3 and m >= 3:
            return 'Promising'
        
        # Need Attention: Average across all metrics
        elif r >= 2 and f >= 2 and m >= 2:
            return 'Need Attention'
        
        # About to Sleep: Below average
        elif r <= 2 and f <= 3:
            return 'About to Sleep'
        
        # At Risk: Low recency, was frequent
        elif r <= 2 and f >= 4:
            return 'At Risk'
        
        # Can't Lose Them: Low recency, high monetary
        elif r <= 2 and m >= 4:
            return "Can't Lose Them"
        
        # Lost: Low scores across the board
        else:
            return 'Lost'
    
    @staticmethod
    def get_segment_summary(rfm_df):
        """Get summary statistics by segment"""
        try:
            summary = rfm_df.groupby('Segment').agg({
                'Recency': 'mean',
                'Frequency': 'mean',
                'Monetary': ['mean', 'sum'],
                'Segment': 'count'
            }).round(2)
            
            summary.columns = ['Avg_Recency', 'Avg_Frequency', 'Avg_Monetary', 'Total_Monetary', 'Customer_Count']
            summary = summary.reset_index()
            summary = summary.sort_values('Customer_Count', ascending=False)
            
            return summary, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def calculate_customer_lifetime_value(rfm_df):
        """Calculate Customer Lifetime Value (CLV)"""
        try:
            # Simple CLV = Frequency * Monetary
            rfm_copy = rfm_df.copy()
            rfm_copy['CLV'] = rfm_copy['Frequency'] * rfm_copy['Monetary']
            rfm_copy = rfm_copy.sort_values('CLV', ascending=False)
            
            return rfm_copy, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def cohort_analysis(df, customer_col, date_col):
        """
        Perform cohort analysis
        
        Parameters:
        -----------
        df : DataFrame
            Transaction data
        customer_col : str
            Customer ID column
        date_col : str
            Date column
        
        Returns:
        --------
        cohort_df : DataFrame
            Cohort analysis matrix
        """
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            
            # Get first purchase date for each customer
            df_copy['CohortMonth'] = df_copy.groupby(customer_col)[date_col].transform('min').dt.to_period('M')
            df_copy['PurchaseMonth'] = df_copy[date_col].dt.to_period('M')
            
            # Calculate cohort index (months since first purchase)
            df_copy['CohortIndex'] = (df_copy['PurchaseMonth'] - df_copy['CohortMonth']).apply(lambda x: x.n)
            
            # Count unique customers per cohort and period
            cohort_data = df_copy.groupby(['CohortMonth', 'CohortIndex'])[customer_col].nunique().reset_index()
            cohort_data.columns = ['CohortMonth', 'CohortIndex', 'CustomerCount']
            
            # Pivot to create cohort matrix
            cohort_matrix = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerCount')
            
            # Calculate retention rates
            cohort_size = cohort_matrix.iloc[:, 0]
            retention_matrix = cohort_matrix.divide(cohort_size, axis=0) * 100
            
            return retention_matrix.round(2), None
        
        except Exception as e:
            return None, str(e)
