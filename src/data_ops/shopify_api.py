"""
Shopify API Integration
Connect to Shopify stores and fetch e-commerce data

SEPARATION OF CONCERNS: Shopify-specific API integration only
"""

import pandas as pd
from data_ops.api_connector import APIConnector, APIResponseHandler
from datetime import datetime, timedelta


class ShopifyAPI:
    """Shopify API connector for e-commerce data analysis"""
    
    def __init__(self, shop_name, api_key, api_password, api_version='2024-10'):
        """
        Initialize Shopify API connector
        
        Parameters:
        -----------
        shop_name : str
            Shopify store name (e.g., 'mystore' for mystore.myshopify.com)
        api_key : str
            Shopify API key (not used in requests, for reference only)
        api_password : str
            Shopify Admin API access token (starts with shpat_ or shppa_)
        api_version : str
            Shopify API version (default: 2024-10, latest stable)
        """
        self.shop_name = shop_name
        self.api_key = api_key
        self.api_version = api_version
        
        # Build base URL (no credentials embedded)
        base_url = f"https://{shop_name}.myshopify.com/admin/api/{api_version}"
        
        # Shopify requires X-Shopify-Access-Token header
        headers = {
            'X-Shopify-Access-Token': api_password,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Initialize API connector with custom headers
        # IMPORTANT: Pass api_key=None to prevent Bearer auth header
        self.connector = APIConnector(base_url=base_url, api_key=None, headers=headers)
        self.connector.min_request_interval = 0.5  # Shopify rate limit: 2 requests/second
    
    def test_connection(self):
        """
        Test Shopify API connection
        
        Returns:
        --------
        success : bool
        message : str
        """
        success, data, error = self.connector.get('shop.json')
        
        if success:
            shop_name = data.get('shop', {}).get('name', 'Unknown')
            return True, f"Successfully connected to: {shop_name}"
        else:
            return False, f"Connection failed: {error}"
    
    def get_orders(self, status='any', limit=250, created_at_min=None, created_at_max=None):
        """
        Fetch orders from Shopify
        
        Parameters:
        -----------
        status : str
            Order status ('any', 'open', 'closed', 'cancelled')
        limit : int
            Number of orders to fetch per page (max 250)
        created_at_min : str
            Minimum creation date (ISO format)
        created_at_max : str
            Maximum creation date (ISO format)
        
        Returns:
        --------
        df : DataFrame
        error : str or None
        """
        try:
            # Build parameters
            params = {
                'status': status,
                'limit': min(limit, 250)
            }
            
            if created_at_min:
                params['created_at_min'] = created_at_min
            if created_at_max:
                params['created_at_max'] = created_at_max
            
            # Fetch orders with pagination
            success, orders_data, error = self.connector.fetch_paginated(
                'orders.json',
                params=params,
                page_param='page',
                per_page_param='limit',
                per_page=250
            )
            
            if not success:
                return None, error
            
            # Extract orders from response
            orders = []
            for item in orders_data:
                if 'orders' in item:
                    orders.extend(item['orders'])
                else:
                    orders.append(item)
            
            # Convert to DataFrame
            df = pd.DataFrame(orders)
            
            # Clean and format data
            if not df.empty:
                df = self._process_orders_dataframe(df)
            
            return df, None
        
        except Exception as e:
            return None, f"Error fetching orders: {str(e)}"
    
    def get_products(self, limit=250):
        """
        Fetch products from Shopify
        
        Parameters:
        -----------
        limit : int
            Number of products per page (max 250)
        
        Returns:
        --------
        df : DataFrame
        error : str or None
        """
        try:
            # Fetch products with pagination
            success, products_data, error = self.connector.fetch_paginated(
                'products.json',
                params={'limit': min(limit, 250)},
                page_param='page',
                per_page_param='limit',
                per_page=250
            )
            
            if not success:
                return None, error
            
            # Extract products
            products = []
            for item in products_data:
                if 'products' in item:
                    products.extend(item['products'])
                else:
                    products.append(item)
            
            # Convert to DataFrame
            df = pd.DataFrame(products)
            
            # Clean and format data
            if not df.empty:
                df = self._process_products_dataframe(df)
            
            return df, None
        
        except Exception as e:
            return None, f"Error fetching products: {str(e)}"
    
    def get_customers(self, limit=250):
        """
        Fetch customers from Shopify
        
        Parameters:
        -----------
        limit : int
            Number of customers per page (max 250)
        
        Returns:
        --------
        df : DataFrame
        error : str or None
        """
        try:
            # Fetch customers with pagination
            success, customers_data, error = self.connector.fetch_paginated(
                'customers.json',
                params={'limit': min(limit, 250)},
                page_param='page',
                per_page_param='limit',
                per_page=250
            )
            
            if not success:
                return None, error
            
            # Extract customers
            customers = []
            for item in customers_data:
                if 'customers' in item:
                    customers.extend(item['customers'])
                else:
                    customers.append(item)
            
            # Convert to DataFrame
            df = pd.DataFrame(customers)
            
            # Clean and format data
            if not df.empty:
                df = self._process_customers_dataframe(df)
            
            return df, None
        
        except Exception as e:
            return None, f"Error fetching customers: {str(e)}"
    
    def get_inventory(self):
        """
        Fetch inventory levels from Shopify
        
        Returns:
        --------
        df : DataFrame
        error : str or None
        """
        try:
            success, data, error = self.connector.fetch_paginated(
                'inventory_levels.json',
                params={'limit': 250},
                page_param='page',
                per_page_param='limit',
                per_page=250
            )
            
            if not success:
                return None, error
            
            # Extract inventory levels
            inventory = []
            for item in data:
                if 'inventory_levels' in item:
                    inventory.extend(item['inventory_levels'])
                else:
                    inventory.append(item)
            
            df = pd.DataFrame(inventory)
            return df, None
        
        except Exception as e:
            return None, f"Error fetching inventory: {str(e)}"
    
    def _process_orders_dataframe(self, df):
        """Process and clean orders DataFrame"""
        # Extract key columns
        key_columns = ['id', 'order_number', 'email', 'created_at', 'updated_at', 
                      'total_price', 'subtotal_price', 'total_tax', 'currency',
                      'financial_status', 'fulfillment_status', 'customer']
        
        # Keep only existing columns
        existing_cols = [col for col in key_columns if col in df.columns]
        if existing_cols:
            df = df[existing_cols]
        
        # Parse dates
        date_columns = ['created_at', 'updated_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['total_price', 'subtotal_price', 'total_tax']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Extract customer info if available
        if 'customer' in df.columns:
            df['customer_id'] = df['customer'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            df['customer_email'] = df['customer'].apply(lambda x: x.get('email') if isinstance(x, dict) else None)
            df = df.drop('customer', axis=1)
        
        return df
    
    def _process_products_dataframe(self, df):
        """Process and clean products DataFrame"""
        # Extract key columns
        key_columns = ['id', 'title', 'vendor', 'product_type', 'created_at', 
                      'updated_at', 'published_at', 'status', 'variants']
        
        existing_cols = [col for col in key_columns if col in df.columns]
        if existing_cols:
            df = df[existing_cols]
        
        # Parse dates
        date_columns = ['created_at', 'updated_at', 'published_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Extract variant info
        if 'variants' in df.columns:
            df['variant_count'] = df['variants'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            df['price'] = df['variants'].apply(lambda x: x[0].get('price') if isinstance(x, list) and len(x) > 0 else None)
            df = df.drop('variants', axis=1)
        
        return df
    
    def _process_customers_dataframe(self, df):
        """Process and clean customers DataFrame"""
        # Extract key columns
        key_columns = ['id', 'email', 'first_name', 'last_name', 'orders_count', 
                      'total_spent', 'created_at', 'updated_at', 'state']
        
        existing_cols = [col for col in key_columns if col in df.columns]
        if existing_cols:
            df = df[existing_cols]
        
        # Parse dates
        date_columns = ['created_at', 'updated_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['orders_count', 'total_spent']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df


class ShopifyDataAnalyzer:
    """Helper class for analyzing Shopify data"""
    
    @staticmethod
    def calculate_sales_metrics(orders_df):
        """Calculate sales metrics from orders DataFrame"""
        if orders_df is None or orders_df.empty:
            return None
        
        metrics = {
            'total_orders': len(orders_df),
            'total_revenue': orders_df['total_price'].sum() if 'total_price' in orders_df.columns else 0,
            'average_order_value': orders_df['total_price'].mean() if 'total_price' in orders_df.columns else 0,
            'total_tax': orders_df['total_tax'].sum() if 'total_tax' in orders_df.columns else 0,
        }
        
        return metrics
    
    @staticmethod
    def analyze_customer_behavior(customers_df):
        """Analyze customer behavior from customers DataFrame"""
        if customers_df is None or customers_df.empty:
            return None
        
        metrics = {
            'total_customers': len(customers_df),
            'total_orders': customers_df['orders_count'].sum() if 'orders_count' in customers_df.columns else 0,
            'average_orders_per_customer': customers_df['orders_count'].mean() if 'orders_count' in customers_df.columns else 0,
            'total_customer_value': customers_df['total_spent'].sum() if 'total_spent' in customers_df.columns else 0,
            'average_customer_value': customers_df['total_spent'].mean() if 'total_spent' in customers_df.columns else 0,
        }
        
        return metrics
    
    @staticmethod
    def get_top_products(orders_df, top_n=10):
        """Get top selling products from orders"""
        # This would require line_items data from orders
        # Simplified version here
        return None
