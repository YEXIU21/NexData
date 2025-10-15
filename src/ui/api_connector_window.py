"""
API Connector Window
UI for connecting to various APIs and fetching data

SEPARATION OF CONCERNS: API connection UI only
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from data_ops.api_connector import APIConnector
from data_ops.shopify_api import ShopifyAPI, ShopifyDataAnalyzer
from ui.progress_window import run_with_progress


class APIConnectorWindow:
    """Window for API connections and data fetching"""
    
    def __init__(self, parent, app_callback):
        """
        Initialize API Connector Window
        
        Parameters:
        -----------
        parent : tk.Tk
            Parent window
        app_callback : function
            Callback to pass data back to main app
        """
        self.parent = parent
        self.app_callback = app_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("API Connector")
        self.window.geometry("700x650")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Create UI components"""
        # Main notebook for different API types
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Shopify API Tab
        shopify_frame = ttk.Frame(notebook, padding=20)
        notebook.add(shopify_frame, text="Shopify API")
        self.create_shopify_tab(shopify_frame)
        
        # Generic REST API Tab
        generic_frame = ttk.Frame(notebook, padding=20)
        notebook.add(generic_frame, text="Generic REST API")
        self.create_generic_tab(generic_frame)
        
        # Status bar
        self.status_bar = ttk.Label(self.window, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_shopify_tab(self, parent):
        """Create Shopify API configuration tab"""
        # Title
        ttk.Label(parent, text="Shopify Store Configuration", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(parent, text="Store Credentials", padding=15)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Store name
        ttk.Label(config_frame, text="Store Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.shopify_store = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.shopify_store, width=40).grid(row=0, column=1, pady=5, padx=5)
        ttk.Label(config_frame, text=".myshopify.com", foreground="gray").grid(row=0, column=2, sticky='w')
        
        # API Key
        ttk.Label(config_frame, text="API Key (optional):").grid(row=1, column=0, sticky='w', pady=5)
        self.shopify_api_key = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.shopify_api_key, width=40).grid(row=1, column=1, pady=5, padx=5)
        ttk.Label(config_frame, text="Admin API key", foreground="gray", font=('TkDefaultFont', 8)).grid(row=1, column=2, sticky='w')
        
        # API Password (Access Token)
        ttk.Label(config_frame, text="Access Token:").grid(row=2, column=0, sticky='w', pady=5)
        self.shopify_password = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.shopify_password, width=40, show="*").grid(row=2, column=1, pady=5, padx=5)
        ttk.Label(config_frame, text="Starts with shpat_", foreground="gray", font=('TkDefaultFont', 8)).grid(row=2, column=2, sticky='w')
        
        # API Version
        ttk.Label(config_frame, text="API Version:").grid(row=3, column=0, sticky='w', pady=5)
        self.shopify_version = tk.StringVar(value='2024-10')
        ttk.Combobox(config_frame, textvariable=self.shopify_version, 
                    values=['2024-10', '2025-01', '2024-07', '2024-04', '2024-01', '2023-10'], width=37).grid(row=3, column=1, pady=5, padx=5)
        
        # Test connection button
        ttk.Button(config_frame, text="Test Connection", command=self.test_shopify_connection).grid(row=4, column=1, pady=10)
        
        # Data fetching frame
        fetch_frame = ttk.LabelFrame(parent, text="Fetch Data", padding=15)
        fetch_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Data type selection
        ttk.Label(fetch_frame, text="Data Type:").grid(row=0, column=0, sticky='w', pady=5)
        self.shopify_data_type = tk.StringVar(value='orders')
        data_types = ['orders', 'products', 'customers', 'inventory']
        ttk.Combobox(fetch_frame, textvariable=self.shopify_data_type, values=data_types, width=30).grid(row=0, column=1, pady=5, padx=5)
        
        # Date range for orders
        ttk.Label(fetch_frame, text="Date Range (Orders):").grid(row=1, column=0, sticky='w', pady=5)
        date_frame = ttk.Frame(fetch_frame)
        date_frame.grid(row=1, column=1, pady=5, padx=5, sticky='w')
        
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT)
        self.shopify_date_from = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.shopify_date_from, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT)
        self.shopify_date_to = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.shopify_date_to, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(fetch_frame, text="(Format: YYYY-MM-DD)", foreground="gray").grid(row=2, column=1, sticky='w', padx=5)
        
        # Fetch button
        ttk.Button(fetch_frame, text="Fetch Data", command=self.fetch_shopify_data, 
                  style='Action.TButton').grid(row=3, column=1, pady=15)
        
        # Result label
        self.shopify_result = ttk.Label(fetch_frame, text="", foreground="blue")
        self.shopify_result.grid(row=4, column=0, columnspan=2, pady=5)
    
    def create_generic_tab(self, parent):
        """Create generic REST API configuration tab"""
        # Title
        ttk.Label(parent, text="Generic REST API Configuration", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(parent, text="API Configuration", padding=15)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Base URL
        ttk.Label(config_frame, text="Base URL:").grid(row=0, column=0, sticky='w', pady=5)
        self.api_base_url = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.api_base_url, width=50).grid(row=0, column=1, pady=5, padx=5)
        
        # API Key
        ttk.Label(config_frame, text="API Key (optional):").grid(row=1, column=0, sticky='w', pady=5)
        self.api_key = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.api_key, width=50).grid(row=1, column=1, pady=5, padx=5)
        
        # Endpoint
        ttk.Label(config_frame, text="Endpoint:").grid(row=2, column=0, sticky='w', pady=5)
        self.api_endpoint = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.api_endpoint, width=50).grid(row=2, column=1, pady=5, padx=5)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(parent, text="Query Parameters (Optional)", padding=15)
        params_frame.pack(fill=tk.X, pady=10)
        
        # Parameters text area
        ttk.Label(params_frame, text="One parameter per line (key=value):").pack(anchor='w', pady=5)
        self.api_params_text = tk.Text(params_frame, height=5, width=60)
        self.api_params_text.pack(pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Test Connection", command=self.test_generic_api).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Fetch Data", command=self.fetch_generic_data, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        # Result label
        self.generic_result = ttk.Label(parent, text="", foreground="blue")
        self.generic_result.pack(pady=5)
    
    def test_shopify_connection(self):
        """Test Shopify API connection"""
        try:
            # Validate inputs
            if not all([self.shopify_store.get(), self.shopify_api_key.get(), self.shopify_password.get()]):
                messagebox.showwarning("Missing Information", "Please fill in all required fields")
                return
            
            # Create Shopify API instance
            api = ShopifyAPI(
                self.shopify_store.get().strip(),
                self.shopify_api_key.get().strip(),
                self.shopify_password.get().strip(),
                self.shopify_version.get().strip()
            )
            
            # Test connection
            self.status_bar.config(text="Testing connection...")
            self.window.update()
            
            success, message = api.test_connection()
            
            if success:
                messagebox.showinfo("Success", message)
                self.status_bar.config(text=message)
            else:
                messagebox.showerror("Connection Failed", message)
                self.status_bar.config(text="Connection failed")
        
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed:\n{str(e)}")
            self.status_bar.config(text="Error")
    
    def fetch_shopify_data(self):
        """Fetch data from Shopify with progress tracking"""
        try:
            # Validate inputs
            if not all([self.shopify_store.get(), self.shopify_api_key.get(), self.shopify_password.get()]):
                messagebox.showwarning("Missing Information", "Please fill in all required fields")
                return
            
            # Get parameters
            store = self.shopify_store.get().strip()
            api_key = self.shopify_api_key.get().strip()
            password = self.shopify_password.get().strip()
            version = self.shopify_version.get().strip()
            data_type = self.shopify_data_type.get().strip()
            date_from = self.shopify_date_from.get() or None
            date_to = self.shopify_date_to.get() or None
            
            # Update initial status
            self.shopify_result.config(text="Fetching data...", foreground="blue")
            self.status_bar.config(text="Fetching data...")
            self.window.update()
            
            # Define task function for progress tracking
            def fetch_task(progress):
                # Create API instance
                progress(10, "Connecting to Shopify...", f"Store: {store}")
                api = ShopifyAPI(store, api_key, password, version)
                
                # Fetch data based on type
                progress(30, f"Fetching {data_type}...", "Retrieving data from API")
                
                if data_type == 'orders':
                    df, error = api.get_orders(
                        created_at_min=date_from,
                        created_at_max=date_to
                    )
                elif data_type == 'products':
                    df, error = api.get_products()
                elif data_type == 'customers':
                    df, error = api.get_customers()
                elif data_type == 'inventory':
                    df, error = api.get_inventory()
                else:
                    raise ValueError(f"Unknown data type: {data_type}")
                
                if error:
                    raise Exception(error)
                
                progress(80, "Processing data...", f"Retrieved {len(df) if df is not None else 0} records")
                
                # Small delay for UI feedback
                import time
                time.sleep(0.3)
                
                progress(100, "Complete!", f"Loaded {len(df)} records")
                
                return df
            
            # Run with progress window
            df = run_with_progress(
                self.window,
                fetch_task,
                title=f"Fetching Shopify {data_type.title()}",
                cancelable=False
            )
            
            if df is None or df.empty:
                messagebox.showwarning("No Data", "No data found for the specified criteria")
                self.shopify_result.config(text="No data found", foreground="orange")
                return
            
            # Success - pass data back to main app
            self.shopify_result.config(text=f"Success! Fetched {len(df)} records", foreground="green")
            self.status_bar.config(text=f"Successfully fetched {len(df)} {data_type}")
            
            # Ask if user wants to load into main app
            if messagebox.askyesno("Data Fetched", 
                                  f"Successfully fetched {len(df)} {data_type} records.\nLoad into main application?"):
                self.app_callback(df)
                self.window.destroy()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data:\n{str(e)}")
            self.shopify_result.config(text=f"Error: {str(e)}", foreground="red")
    
    def test_generic_api(self):
        """Test generic API connection"""
        try:
            # Validate inputs
            if not self.api_base_url.get():
                messagebox.showwarning("Missing Information", "Please enter the base URL")
                return
            
            # Create API connector
            api = APIConnector(
                self.api_base_url.get(),
                self.api_key.get() or None
            )
            
            # Test with a simple endpoint or root
            endpoint = self.api_endpoint.get() or ''
            
            self.status_bar.config(text="Testing connection...")
            self.window.update()
            
            success, data, error = api.get(endpoint)
            
            if success:
                messagebox.showinfo("Success", f"Connection successful!\nReceived data: {type(data)}")
                self.status_bar.config(text="Connection successful")
            else:
                messagebox.showerror("Connection Failed", error)
                self.status_bar.config(text="Connection failed")
        
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed:\n{str(e)}")
            self.status_bar.config(text="Error")
    
    def fetch_generic_data(self):
        """Fetch data from generic API"""
        try:
            # Validate inputs
            if not all([self.api_base_url.get(), self.api_endpoint.get()]):
                messagebox.showwarning("Missing Information", "Please enter base URL and endpoint")
                return
            
            # Parse parameters
            params = {}
            params_text = self.api_params_text.get("1.0", tk.END).strip()
            if params_text:
                for line in params_text.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        params[key.strip()] = value.strip()
            
            # Create API connector
            api = APIConnector(
                self.api_base_url.get(),
                self.api_key.get() or None
            )
            
            # Update status
            self.generic_result.config(text="Fetching data...", foreground="blue")
            self.status_bar.config(text="Fetching data...")
            self.window.update()
            
            # Fetch data
            success, data, error = api.get(self.api_endpoint.get(), params=params if params else None)
            
            if not success:
                messagebox.showerror("Error", f"Failed to fetch data:\n{error}")
                self.generic_result.config(text=f"Error: {error}", foreground="red")
                return
            
            # Convert to DataFrame
            df, df_error = api.to_dataframe(data)
            
            if df_error:
                messagebox.showerror("Error", f"Failed to convert data:\n{df_error}")
                self.generic_result.config(text=f"Error: {df_error}", foreground="red")
                return
            
            if df is None or df.empty:
                messagebox.showwarning("No Data", "No data found")
                self.generic_result.config(text="No data found", foreground="orange")
                return
            
            # Success
            self.generic_result.config(text=f"Success! Fetched {len(df)} records", foreground="green")
            self.status_bar.config(text=f"Successfully fetched {len(df)} records")
            
            # Ask if user wants to load into main app
            if messagebox.askyesno("Data Fetched", 
                                  f"Successfully fetched {len(df)} records.\nLoad into main application?"):
                self.app_callback(df)
                self.window.destroy()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data:\n{str(e)}")
            self.generic_result.config(text=f"Error: {str(e)}", foreground="red")
