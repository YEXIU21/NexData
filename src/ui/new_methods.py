"""
New method implementations for NexData
This file contains all new feature methods to be integrated into main_window.py
"""

# NOTE: These methods should be added to the DataAnalystApp class in main_window.py

def pivot_table(self):
    """Create pivot table"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from analysis.pivot_table import PivotTableGenerator
    
    dialog = tk.Toplevel(self.root)
    dialog.title("Pivot Table Generator")
    dialog.geometry("500x400")
    
    ttk.Label(dialog, text="Create Pivot Table", font=('Arial', 12, 'bold')).pack(pady=10)
    
    # Index columns
    ttk.Label(dialog, text="Index (Rows):").pack(pady=5)
    index_frame = ttk.Frame(dialog)
    index_frame.pack(pady=5)
    index_listbox = tk.Listbox(index_frame, selectmode='multiple', height=5)
    for col in self.df.columns:
        index_listbox.insert(tk.END, col)
    index_listbox.pack()
    
    # Column columns
    ttk.Label(dialog, text="Columns:").pack(pady=5)
    column_frame = ttk.Frame(dialog)
    column_frame.pack(pady=5)
    column_listbox = tk.Listbox(column_frame, selectmode='multiple', height=5)
    for col in self.df.columns:
        column_listbox.insert(tk.END, col)
    column_listbox.pack()
    
    # Value column
    ttk.Label(dialog, text="Values:").pack(pady=5)
    numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        messagebox.showerror("Error", "No numeric columns found!")
        dialog.destroy()
        return
    
    value_var = tk.StringVar(value=numeric_cols[0])
    ttk.Combobox(dialog, textvariable=value_var, values=numeric_cols, state='readonly').pack(pady=5)
    
    # Aggregation function
    ttk.Label(dialog, text="Aggregation:").pack(pady=5)
    agg_funcs = list(PivotTableGenerator.get_aggregation_functions().values())
    agg_var = tk.StringVar(value='Sum')
    ttk.Combobox(dialog, textvariable=agg_var, values=agg_funcs, state='readonly').pack(pady=5)
    
    def create_pivot():
        index_cols = [index_listbox.get(i) for i in index_listbox.curselection()]
        column_cols = [column_listbox.get(i) for i in column_listbox.curselection()]
        
        agg_map = {v: k for k, v in PivotTableGenerator.get_aggregation_functions().items()}
        agg_func = agg_map[agg_var.get()]
        
        pivot_df, error = PivotTableGenerator.create_pivot(
            self.df, index_cols, column_cols, value_var.get(), agg_func
        )
        
        if error:
            messagebox.showerror("Error", error)
        else:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"=== PIVOT TABLE ===\n\n{pivot_df.to_string()}")
            self.notebook.select(0)
            self.update_status("Pivot table created")
            dialog.destroy()
    
    ttk.Button(dialog, text="Create Pivot", command=create_pivot).pack(pady=15)

def advanced_filters(self):
    """Apply advanced filters"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    messagebox.showinfo("Advanced Filters", 
                       "Use Analysis > SQL Query for advanced filtering.\n\n" +
                       "Example: SELECT * FROM data WHERE column > 100")

def data_quality_check(self):
    """Run data quality assessment"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from data_ops.data_quality import DataQualityChecker
    
    self.perf_monitor.start_operation('data_quality_check')
    
    quality_report = DataQualityChecker.assess_quality(self.df)
    report_text = DataQualityChecker.generate_quality_report_text(quality_report)
    
    self.output_text.delete(1.0, tk.END)
    self.output_text.insert(tk.END, report_text)
    self.notebook.select(0)
    
    self.perf_monitor.end_operation('data_quality_check')
    self.update_status(f"Data quality: {quality_report['quality_level']} ({quality_report['overall_score']:.0f}/100)")

def auto_insights(self):
    """Generate automated insights"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from analysis.auto_insights import AutoInsights
    
    insights = AutoInsights.generate_insights(self.df)
    
    output = f"\n{'='*60}\nAUTO-GENERATED INSIGHTS\n{'='*60}\n\n"
    
    output += "SUMMARY:\n"
    for item in insights['summary']:
        output += f"• {item}\n"
    
    if insights['trends']:
        output += "\nTRENDS:\n"
        for item in insights['trends']:
            output += f"• {item}\n"
    
    if insights['correlations']:
        output += "\nCORRELATIONS:\n"
        for item in insights['correlations']:
            output += f"• {item}\n"
    
    if insights['recommendations']:
        output += "\nRECOMMENDATIONS:\n"
        for item in insights['recommendations']:
            output += f"✓ {item}\n"
    
    self.output_text.delete(1.0, tk.END)
    self.output_text.insert(tk.END, output)
    self.notebook.select(0)
    self.update_status("Auto insights generated")

def rfm_segmentation(self):
    """RFM Customer Segmentation"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from analysis.rfm_segmentation import RFMSegmentation
    
    dialog = tk.Toplevel(self.root)
    dialog.title("RFM Customer Segmentation")
    dialog.geometry("400x300")
    
    ttk.Label(dialog, text="RFM Analysis", font=('Arial', 12, 'bold')).pack(pady=10)
    
    all_cols = list(self.df.columns)
    
    ttk.Label(dialog, text="Customer ID Column:").pack(pady=5)
    customer_var = tk.StringVar(value=all_cols[0])
    ttk.Combobox(dialog, textvariable=customer_var, values=all_cols, state='readonly').pack(pady=5)
    
    ttk.Label(dialog, text="Date Column:").pack(pady=5)
    date_var = tk.StringVar(value=all_cols[0])
    ttk.Combobox(dialog, textvariable=date_var, values=all_cols, state='readonly').pack(pady=5)
    
    numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
    
    ttk.Label(dialog, text="Revenue Column:").pack(pady=5)
    revenue_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else all_cols[0])
    ttk.Combobox(dialog, textvariable=revenue_var, values=numeric_cols, state='readonly').pack(pady=5)
    
    def calculate():
        rfm_df, error = RFMSegmentation.calculate_rfm(
            self.df, customer_var.get(), date_var.get(), revenue_var.get()
        )
        
        if error:
            messagebox.showerror("Error", error)
        else:
            summary, _ = RFMSegmentation.get_segment_summary(rfm_df)
            
            output = f"=== RFM CUSTOMER SEGMENTATION ===\n\n"
            output += f"SEGMENT SUMMARY:\n\n{summary.to_string()}\n\n"
            output += f"DETAILED RFM SCORES (First 20):\n\n{rfm_df.head(20).to_string()}"
            
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, output)
            self.notebook.select(0)
            self.update_status(f"RFM analysis complete: {len(rfm_df)} customers segmented")
            dialog.destroy()
    
    ttk.Button(dialog, text="Calculate RFM", command=calculate).pack(pady=15)

def time_series_forecasting(self):
    """Time series forecasting"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from analysis.forecasting import TimeSeriesForecasting
    
    dialog = tk.Toplevel(self.root)
    dialog.title("Time Series Forecasting")
    dialog.geometry("400x300")
    
    ttk.Label(dialog, text="Forecasting", font=('Arial', 12, 'bold')).pack(pady=10)
    
    all_cols = list(self.df.columns)
    numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
    
    ttk.Label(dialog, text="Date Column:").pack(pady=5)
    date_var = tk.StringVar(value=all_cols[0])
    ttk.Combobox(dialog, textvariable=date_var, values=all_cols, state='readonly').pack(pady=5)
    
    ttk.Label(dialog, text="Value Column:").pack(pady=5)
    value_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else all_cols[0])
    ttk.Combobox(dialog, textvariable=value_var, values=numeric_cols, state='readonly').pack(pady=5)
    
    ttk.Label(dialog, text="Method:").pack(pady=5)
    method_var = tk.StringVar(value='Linear Trend')
    ttk.Combobox(dialog, textvariable=method_var, values=['Linear Trend', 'Moving Average', 'Exponential Smoothing'], state='readonly').pack(pady=5)
    
    ttk.Label(dialog, text="Forecast Periods:").pack(pady=5)
    periods_var = tk.IntVar(value=30)
    ttk.Spinbox(dialog, from_=1, to=365, textvariable=periods_var).pack(pady=5)
    
    def forecast():
        method = method_var.get()
        
        if method == 'Linear Trend':
            result, trend_info, error = TimeSeriesForecasting.linear_trend_forecast(
                self.df, date_var.get(), value_var.get(), periods_var.get()
            )
            if error:
                messagebox.showerror("Error", error)
                return
            
            output = f"=== LINEAR TREND FORECAST ===\n\n"
            if trend_info:
                output += f"Trend: {trend_info['direction']}\n"
                output += f"Daily Change: {trend_info['daily_change']:.4f}\n"
                output += f"R²: {trend_info['r_squared']:.4f}\n\n"
            
        elif method == 'Moving Average':
            result, error = TimeSeriesForecasting.simple_moving_average(
                self.df, date_var.get(), value_var.get(), 7, periods_var.get()
            )
            if error:
                messagebox.showerror("Error", error)
                return
            output = f"=== MOVING AVERAGE FORECAST ===\n\n"
        
        else:  # Exponential Smoothing
            result, error = TimeSeriesForecasting.exponential_smoothing(
                self.df, date_var.get(), value_var.get(), 0.3, periods_var.get()
            )
            if error:
                messagebox.showerror("Error", error)
                return
            output = f"=== EXPONENTIAL SMOOTHING FORECAST ===\n\n"
        
        output += f"Forecast (Last 10 periods):\n\n{result.tail(10).to_string()}"
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output)
        self.notebook.select(0)
        self.update_status("Forecast generated")
        dialog.destroy()
    
    ttk.Button(dialog, text="Generate Forecast", command=forecast).pack(pady=15)

def sales_dashboard(self):
    """Sales analytics dashboard"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from analysis.dashboard_templates import DashboardTemplates
    
    # Simple column selection dialog
    all_cols = list(self.df.columns)
    numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
    
    date_col = simpledialog.askstring("Sales Dashboard", f"Enter date column:\n{', '.join(all_cols[:5])}")
    revenue_col = simpledialog.askstring("Sales Dashboard", f"Enter revenue column:\n{', '.join(numeric_cols[:5])}")
    
    if date_col and revenue_col:
        dashboard, error = DashboardTemplates.sales_dashboard(self.df, date_col, revenue_col)
        
        if error:
            messagebox.showerror("Error", error)
        else:
            report = DashboardTemplates.format_dashboard_report(dashboard, 'sales')
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, report)
            self.notebook.select(0)
            self.update_status("Sales dashboard generated")

def customer_dashboard(self):
    """Customer analytics dashboard"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from analysis.dashboard_templates import DashboardTemplates
    
    all_cols = list(self.df.columns)
    numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
    
    customer_col = simpledialog.askstring("Customer Dashboard", f"Enter customer column:\n{', '.join(all_cols[:5])}")
    date_col = simpledialog.askstring("Customer Dashboard", f"Enter date column:\n{', '.join(all_cols[:5])}")
    revenue_col = simpledialog.askstring("Customer Dashboard", f"Enter revenue column:\n{', '.join(numeric_cols[:5])}")
    
    if customer_col and date_col and revenue_col:
        dashboard, error = DashboardTemplates.customer_dashboard(self.df, customer_col, date_col, revenue_col)
        
        if error:
            messagebox.showerror("Error", error)
        else:
            report = DashboardTemplates.format_dashboard_report(dashboard, 'customer')
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, report)
            self.notebook.select(0)
            self.update_status("Customer dashboard generated")

def compare_datasets(self):
    """Compare two datasets"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from data_ops.data_comparison import DataComparison
    
    # Ask user to load second dataset
    file_path = filedialog.askopenfilename(
        title="Select second dataset to compare",
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
    )
    
    if not file_path:
        return
    
    try:
        if file_path.endswith('.csv'):
            df2 = pd.read_csv(file_path)
        else:
            df2 = pd.read_excel(file_path)
        
        # Compare
        comparison = DataComparison.compare_dataframes(self.df, df2)
        
        output = f"=== DATASET COMPARISON ===\n\n"
        output += f"Dataset 1 Shape: {comparison['df1_shape']}\n"
        output += f"Dataset 2 Shape: {comparison['df2_shape']}\n\n"
        
        output += f"Common Columns ({len(comparison['common_columns'])}):\n"
        output += f"{', '.join(comparison['common_columns'])}\n\n"
        
        if comparison['only_in_df1']:
            output += f"Only in Dataset 1: {', '.join(comparison['only_in_df1'])}\n"
        
        if comparison['only_in_df2']:
            output += f"Only in Dataset 2: {', '.join(comparison['only_in_df2'])}\n"
        
        # Summary comparison
        summary, error = DataComparison.get_summary_comparison(self.df, df2)
        if summary is not None:
            output += f"\n\nNUMERIC COMPARISON:\n\n{summary.to_string()}"
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output)
        self.notebook.select(0)
        self.update_status("Dataset comparison complete")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to compare datasets:\n{str(e)}")

def export_powerpoint(self):
    """Export to PowerPoint"""
    if self.df is None:
        messagebox.showwarning("Warning", "No data loaded!")
        return
    
    from data_ops.pptx_export import PowerPointExporter
    
    # Check if python-pptx is available
    available, msg = PowerPointExporter.check_pptx_available()
    
    if not available:
        messagebox.showwarning("Package Required", msg)
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pptx",
        filetypes=[("PowerPoint files", "*.pptx")]
    )
    
    if file_path:
        success, msg = PowerPointExporter.create_presentation(self.df, file_path)
        
        if success:
            messagebox.showinfo("Success", msg)
            self.update_status("Exported to PowerPoint")
        else:
            messagebox.showerror("Error", msg)

def performance_monitor(self):
    """Show performance monitoring report"""
    report = self.perf_monitor.get_performance_report()
    report_text = self.perf_monitor.format_performance_report(report)
    tips = self.perf_monitor.get_optimization_tips(report)
    
    report_text += "\n=== OPTIMIZATION TIPS ===\n"
    for tip in tips:
        report_text += f"{tip}\n"
    
    self.output_text.delete(1.0, tk.END)
    self.output_text.insert(tk.END, report_text)
    self.notebook.select(0)
    self.update_status("Performance report generated")
