"""
Analysis Dialog Classes
Contains all analysis-related dialogs extracted from main_window.py
Following SEPARATION OF CONCERNS and CLEAN CODE principles
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import pandas as pd


class AnalysisDialogs:
    """Factory class for analysis dialogs"""
    
    @staticmethod
    def show_time_series_dialog(parent, df, create_plot_callback):
        """
        Show time series analysis dialog
        
        Args:
            parent: Parent window
            df: DataFrame to analyze
            create_plot_callback: Callback function(plot_func)
        """
        # Find date columns
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Also check object columns that might be dates
        for col in df.select_dtypes(include=['object']).columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(df[col].head())
                    date_cols.append(col)
                except:
                    pass
        
        if not date_cols:
            messagebox.showwarning("Warning", "No date columns found! Try converting a column to datetime first.")
            return
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns for analysis!")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Time Series Analysis")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="Date Column:", font=('Arial', 11, 'bold')).pack(pady=5)
        date_var = tk.StringVar(value=date_cols[0])
        ttk.Combobox(dialog, textvariable=date_var, values=date_cols, state='readonly', width=30).pack(pady=5)
        
        ttk.Label(dialog, text="Value Column:", font=('Arial', 11, 'bold')).pack(pady=5)
        value_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(dialog, textvariable=value_var, values=numeric_cols, state='readonly', width=30).pack(pady=5)
        
        def analyze():
            date_col = date_var.get()
            value_col = value_var.get()
            
            # Convert to datetime if needed
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col])
            df_temp = df_temp.sort_values(date_col)
            
            def plot_func(fig, ax):
                ax.plot(df_temp[date_col], df_temp[value_col], marker='o', linestyle='-', linewidth=2, markersize=4)
                ax.set_title(f'Time Series: {value_col} over Time', fontsize=14, fontweight='bold')
                ax.set_xlabel('Date')
                ax.set_ylabel(value_col)
                ax.grid(True, alpha=0.3)
                fig.autofmt_xdate()
            
            create_plot_callback(plot_func)
            dialog.destroy()
        
        ttk.Button(dialog, text="Analyze", command=analyze).pack(pady=15)
    
    @staticmethod
    def show_correlation_analysis(df, output_callback):
        """
        Perform correlation analysis and display results
        
        Args:
            df: DataFrame to analyze
            output_callback: Callback function(text) to display output
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            messagebox.showwarning("Warning", "Need at least 2 numeric columns!")
            return
        
        corr_matrix = df[numeric_cols].corr()
        
        output = []
        output.append("=" * 80)
        output.append("CORRELATION ANALYSIS")
        output.append("=" * 80)
        output.append("")
        output.append(corr_matrix.to_string())
        output.append("")
        output.append("=" * 80)
        output.append("💡 Use Visualize > Correlation Heatmap for visual representation")
        
        output_callback("\n".join(output))
    
    @staticmethod
    def show_pivot_table_dialog(parent):
        """Show pivot table dialog (placeholder)"""
        messagebox.showinfo("Coming Soon", "Pivot table will be added in next version!")
    
    @staticmethod
    def show_column_analysis_dialog(parent, df, output_callback, notebook_callback, status_callback):
        """
        Show column analysis dialog
        
        Args:
            parent: Parent window
            df: DataFrame to analyze
            output_callback: Callback function(text) to display output
            notebook_callback: Callback to switch to output tab
            status_callback: Callback to update status
        """
        dialog = tk.Toplevel(parent)
        dialog.title("Column Analysis")
        dialog.geometry("350x150")
        
        ttk.Label(dialog, text="Select column to analyze:", font=('Arial', 11)).pack(pady=10)
        col_var = tk.StringVar(value=df.columns[0])
        ttk.Combobox(dialog, textvariable=col_var, values=list(df.columns), state='readonly', width=30).pack(pady=5)
        
        def analyze():
            col = col_var.get()
            output = []
            output.append("=" * 80)
            output.append(f"COLUMN ANALYSIS: {col}")
            output.append("=" * 80)
            output.append("")
            
            output.append(f"Data Type: {df[col].dtype}")
            output.append(f"Non-Null Count: {df[col].notna().sum():,}")
            output.append(f"Null Count: {df[col].isna().sum():,}")
            output.append(f"Unique Values: {df[col].nunique():,}")
            output.append("")
            
            if pd.api.types.is_numeric_dtype(df[col]):
                output.append("STATISTICS:")
                output.append(f"  Mean: {df[col].mean():.2f}")
                output.append(f"  Median: {df[col].median():.2f}")
                output.append(f"  Std Dev: {df[col].std():.2f}")
                output.append(f"  Min: {df[col].min():.2f}")
                output.append(f"  Max: {df[col].max():.2f}")
                output.append("")
            
            output.append("TOP 10 VALUES:")
            value_counts = df[col].value_counts().head(10)
            output.append(value_counts.to_string())
            
            output_callback("\n".join(output))
            notebook_callback()
            status_callback(f"Column {col} analyzed")
            dialog.destroy()
        
        ttk.Button(dialog, text="Analyze", command=analyze).pack(pady=15)
    
    @staticmethod
    def show_sort_data_dialog(parent, df, analysis_service, output_callback, notebook_callback, 
                             info_panel_callback, status_callback):
        """
        Show sort data dialog
        
        Args:
            parent: Parent window
            df: DataFrame to sort
            analysis_service: Analysis service instance
            output_callback: Callback function(text) to display output
            notebook_callback: Callback to switch to output tab
            info_panel_callback: Callback to update info panel
            status_callback: Callback to update status
        Returns:
            sorted DataFrame or None
        """
        dialog = tk.Toplevel(parent)
        dialog.title("Sort Data")
        dialog.geometry("500x450")
        
        ttk.Label(dialog, text="Sort Data - Advanced", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Primary sort
        ttk.Label(dialog, text="Primary Sort Column:", 
                 font=('Arial', 10, 'bold')).pack(pady=(10,5))
        
        col1_frame = ttk.Frame(dialog)
        col1_frame.pack(pady=5)
        
        col1_var = tk.StringVar(value=df.columns[0])
        ttk.Combobox(col1_frame, textvariable=col1_var, 
                    values=list(df.columns), state='readonly', width=25).pack(side=tk.LEFT, padx=5)
        
        order1_var = tk.StringVar(value="ascending")
        ttk.Radiobutton(col1_frame, text="A→Z / 1→9", 
                       variable=order1_var, value="ascending").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(col1_frame, text="Z→A / 9→1", 
                       variable=order1_var, value="descending").pack(side=tk.LEFT, padx=5)
        
        # Secondary sort (optional)
        ttk.Label(dialog, text="Secondary Sort Column (optional):", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        col2_frame = ttk.Frame(dialog)
        col2_frame.pack(pady=5)
        
        col2_var = tk.StringVar(value="None")
        col2_dropdown = ttk.Combobox(col2_frame, textvariable=col2_var, 
                                     values=["None"] + list(df.columns), 
                                     state='readonly', width=25)
        col2_dropdown.pack(side=tk.LEFT, padx=5)
        
        order2_var = tk.StringVar(value="ascending")
        ttk.Radiobutton(col2_frame, text="A→Z / 1→9", 
                       variable=order2_var, value="ascending").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(col2_frame, text="Z→A / 9→1", 
                       variable=order2_var, value="descending").pack(side=tk.LEFT, padx=5)
        
        # Tertiary sort (optional)
        ttk.Label(dialog, text="Tertiary Sort Column (optional):", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        col3_frame = ttk.Frame(dialog)
        col3_frame.pack(pady=5)
        
        col3_var = tk.StringVar(value="None")
        col3_dropdown = ttk.Combobox(col3_frame, textvariable=col3_var, 
                                     values=["None"] + list(df.columns), 
                                     state='readonly', width=25)
        col3_dropdown.pack(side=tk.LEFT, padx=5)
        
        order3_var = tk.StringVar(value="ascending")
        ttk.Radiobutton(col3_frame, text="A→Z / 1→9", 
                       variable=order3_var, value="ascending").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(col3_frame, text="Z→A / 9→1", 
                       variable=order3_var, value="descending").pack(side=tk.LEFT, padx=5)
        
        # NA handling
        ttk.Label(dialog, text="Handle Missing Values (NA):", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        na_var = tk.StringVar(value="last")
        na_frame = ttk.Frame(dialog)
        na_frame.pack(pady=5)
        
        ttk.Radiobutton(na_frame, text="Put at end", 
                       variable=na_var, value="last").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(na_frame, text="Put at beginning", 
                       variable=na_var, value="first").pack(side=tk.LEFT, padx=10)
        
        # Info label
        ttk.Label(dialog, text="Tip: Multi-column sort applies in order (Primary → Secondary → Tertiary)", 
                 font=('Arial', 8), foreground='gray').pack(pady=10)
        
        result = [None]  # Use list to store result
        
        def sort():
            try:
                # Build column list and order list
                cols = [col1_var.get()]
                orders = [order1_var.get() == "ascending"]
                
                if col2_var.get() != "None":
                    cols.append(col2_var.get())
                    orders.append(order2_var.get() == "ascending")
                
                if col3_var.get() != "None":
                    cols.append(col3_var.get())
                    orders.append(order3_var.get() == "ascending")
                
                # Handle NA position
                na_position = na_var.get()
                
                # Use analysis service
                sorted_df = analysis_service.sort_data(
                    df,
                    cols,
                    ascending=orders
                )
                result[0] = sorted_df
                
                # Output to text area
                output = []
                output.append("=" * 80)
                output.append("SORT DATA - OPERATION COMPLETE")
                output.append("=" * 80)
                output.append("")
                
                sort_desc = " → ".join(cols)
                output.append(f"Sort order: {sort_desc}")
                output.append(f"NA position: {na_position}")
                output.append("")
                
                for i, col in enumerate(cols):
                    order_text = "Ascending (A→Z / 1→9)" if orders[i] else "Descending (Z→A / 9→1)"
                    output.append(f"  Level {i+1}: {col} - {order_text}")
                
                output.append("")
                output.append("=" * 80)
                output.append(f"SUCCESS: Data sorted by {len(cols)} level(s)")
                output.append(f"Total rows: {len(sorted_df)}")
                
                output_callback("\n".join(output))
                notebook_callback()
                info_panel_callback()
                status_callback(f"Sorted by: {sort_desc}")
                
                messagebox.showinfo("Success", 
                                  f"Data sorted successfully!\n\n"
                                  f"Sort order: {sort_desc}\n"
                                  f"NA position: {na_position}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Sort failed:\n{str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Sort Data", command=sort, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to close
        parent.wait_window(dialog)
        return result[0]
    
    @staticmethod
    def show_groupby_dialog(parent, df, output_callback, display_grid_callback, 
                           notebook_callback, status_callback):
        """Show groupby analysis dialog"""
        dialog = tk.Toplevel(parent)
        dialog.title("Group By Analysis")
        dialog.geometry("450x400")
        
        # Group by column
        ttk.Label(dialog, text="Group by column:", font=('Arial', 11, 'bold')).pack(pady=(10,5))
        groupby_var = tk.StringVar(value=df.columns[0])
        ttk.Combobox(dialog, textvariable=groupby_var, values=list(df.columns), 
                     state='readonly', width=35).pack(pady=5)
        
        # Aggregate column
        ttk.Label(dialog, text="Aggregate column:", font=('Arial', 11, 'bold')).pack(pady=(15,5))
        agg_col_var = tk.StringVar(value=df.columns[0])
        ttk.Combobox(dialog, textvariable=agg_col_var, values=list(df.columns), 
                     state='readonly', width=35).pack(pady=5)
        
        # Aggregation function
        ttk.Label(dialog, text="Aggregation function:", font=('Arial', 11, 'bold')).pack(pady=(15,5))
        agg_func_var = tk.StringVar(value="sum")
        func_frame = ttk.Frame(dialog)
        func_frame.pack(pady=5)
        
        functions = [
            ("Sum", "sum"),
            ("Mean", "mean"),
            ("Count", "count"),
            ("Min", "min"),
            ("Max", "max"),
            ("Median", "median")
        ]
        
        for i, (text, value) in enumerate(functions):
            ttk.Radiobutton(func_frame, text=text, variable=agg_func_var, 
                           value=value).grid(row=i//3, column=i%3, padx=10, pady=2)
        
        # Sort order
        ttk.Label(dialog, text="Sort results:", font=('Arial', 11, 'bold')).pack(pady=(15,5))
        sort_var = tk.StringVar(value="descending")
        sort_frame = ttk.Frame(dialog)
        sort_frame.pack(pady=5)
        ttk.Radiobutton(sort_frame, text="Descending (High to Low)", 
                       variable=sort_var, value="descending").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(sort_frame, text="Ascending (Low to High)", 
                       variable=sort_var, value="ascending").pack(side=tk.LEFT, padx=10)
        
        def perform_groupby():
            try:
                group_col = groupby_var.get()
                agg_col = agg_col_var.get()
                agg_func = agg_func_var.get()
                ascending = (sort_var.get() == "ascending")
                
                # Perform groupby
                if agg_func == "count":
                    result = df.groupby(group_col)[agg_col].count()
                elif agg_func == "sum":
                    result = df.groupby(group_col)[agg_col].sum()
                elif agg_func == "mean":
                    result = df.groupby(group_col)[agg_col].mean()
                elif agg_func == "median":
                    result = df.groupby(group_col)[agg_col].median()
                elif agg_func == "min":
                    result = df.groupby(group_col)[agg_col].min()
                elif agg_func == "max":
                    result = df.groupby(group_col)[agg_col].max()
                
                # Sort results
                result = result.sort_values(ascending=ascending)
                
                # Display results - both in text (header) and grid (data)
                output = []
                output.append("=" * 80)
                output.append(f"GROUP BY ANALYSIS: {group_col}")
                output.append(f"Aggregation: {agg_func.upper()}({agg_col})")
                output.append(f"Sort Order: {'Ascending' if ascending else 'Descending'}")
                output.append(f"Total Groups: {len(result)}")
                output.append("=" * 80)
                
                output_callback("\n".join(output))
                
                # Display results in Excel-like grid
                display_grid_callback(
                    result, 
                    title=f"Group By: {group_col} | {agg_func.upper()}({agg_col})"
                )
                
                notebook_callback()
                status_callback(f"Group by {group_col} completed")
                messagebox.showinfo("Success", f"Grouped by {group_col} - {len(result)} groups found")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Group by failed:\n{str(e)}")
        
        ttk.Button(dialog, text="Analyze", command=perform_groupby).pack(pady=20)
    
    @staticmethod
    def show_sql_query_dialog(parent, df, status_callback):
        """Show SQL query dialog"""
        from data_ops.sql_interface import SQLInterface
        
        dialog = tk.Toplevel(parent)
        dialog.title("SQL Query")
        dialog.geometry("800x600")
        
        ttk.Label(dialog, text="Execute SQL Query (table name: 'data')", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Example queries
        ttk.Label(dialog, text="Examples:", font=('Arial', 10, 'bold')).pack(pady=5)
        examples_text = scrolledtext.ScrolledText(dialog, height=4, width=90, wrap=tk.WORD)
        examples_text.pack(pady=5)
        examples_text.insert(tk.END, "SELECT * FROM data LIMIT 10\n")
        examples_text.insert(tk.END, "SELECT column, COUNT(*) FROM data GROUP BY column\n")
        examples_text.insert(tk.END, "SELECT * FROM data WHERE numeric_column > 100\n")
        examples_text.config(state=tk.DISABLED)
        
        # Query input
        ttk.Label(dialog, text="Your SQL Query:").pack(pady=5)
        query_text = scrolledtext.ScrolledText(dialog, height=5, width=90)
        query_text.pack(pady=5)
        query_text.insert(tk.END, "SELECT * FROM data LIMIT 20")
        
        # Result display
        result_label = ttk.Label(dialog, text="Results:")
        result_label.pack(pady=5)
        result_text = scrolledtext.ScrolledText(dialog, height=15, width=90)
        result_text.pack(pady=5)
        
        def execute():
            query = query_text.get(1.0, tk.END).strip()
            
            # Validate query
            is_safe, msg = SQLInterface.validate_query(query)
            if not is_safe:
                messagebox.showerror("Error", msg)
                return
            
            # Execute query
            result_df, error = SQLInterface.execute_query(df, query)
            
            if error:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"ERROR: {error}")
            else:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Rows returned: {len(result_df)}\n\n")
                result_text.insert(tk.END, result_df.to_string())
        
        # Button in centered frame with explicit padding for consistent text positioning
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        exec_btn = ttk.Button(btn_frame, text="Execute Query", command=execute, width=15)
        exec_btn.pack(ipady=2)  # Internal padding to keep text centered vertically
        
        status_callback("SQL Query interface opened")
    
    @staticmethod
    def show_statistical_tests_dialog(parent, df):
        """Show statistical tests dialog"""
        dialog = tk.Toplevel(parent)
        dialog.title("Statistical Tests")
        dialog.geometry("600x500")
        
        ttk.Label(dialog, text="Select Statistical Test", font=('Arial', 14, 'bold')).pack(pady=10)
        
        test_var = tk.StringVar(value="t-test")
        
        ttk.Radiobutton(dialog, text="Independent T-Test (compare 2 groups)", variable=test_var, value="t-test").pack(pady=5)
        ttk.Radiobutton(dialog, text="Paired T-Test (before/after)", variable=test_var, value="paired-t").pack(pady=5)
        ttk.Radiobutton(dialog, text="ANOVA (compare 3+ groups)", variable=test_var, value="anova").pack(pady=5)
        ttk.Radiobutton(dialog, text="Chi-Square Test (categorical)", variable=test_var, value="chi-square").pack(pady=5)
        ttk.Radiobutton(dialog, text="Normality Test", variable=test_var, value="normality").pack(pady=5)
        
        ttk.Label(dialog, text="\nSelect columns:").pack(pady=10)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        frame = ttk.Frame(dialog)
        frame.pack(pady=5)
        
        ttk.Label(frame, text="Column 1:").grid(row=0, column=0, padx=5)
        col1_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else "")
        ttk.Combobox(frame, textvariable=col1_var, values=numeric_cols, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(frame, text="Column 2:").grid(row=1, column=0, padx=5)
        col2_var = tk.StringVar(value=numeric_cols[1] if len(numeric_cols) > 1 else "")
        ttk.Combobox(frame, textvariable=col2_var, values=numeric_cols, width=20).grid(row=1, column=1, padx=5)
        
        result_text = scrolledtext.ScrolledText(dialog, height=10, width=70)
        result_text.pack(pady=10)
        
        def run_test():
            from analysis.statistical_tests import HypothesisTesting
            
            test_type = test_var.get()
            col1 = col1_var.get()
            col2 = col2_var.get()
            
            if not col1 or col1 not in df.columns:
                messagebox.showerror("Error", "Please select valid Column 1")
                return
            
            try:
                result_text.delete(1.0, tk.END)
                
                if test_type == "t-test":
                    if not col2 or col2 not in df.columns:
                        messagebox.showerror("Error", "Please select valid Column 2")
                        return
                    result = HypothesisTesting.t_test_independent(df[col1], df[col2])
                    result_text.insert(tk.END, f"Independent T-Test: {col1} vs {col2}\n\n")
                
                elif test_type == "paired-t":
                    if not col2 or col2 not in df.columns:
                        messagebox.showerror("Error", "Please select valid Column 2")
                        return
                    result = HypothesisTesting.t_test_paired(df[col1], df[col2])
                    result_text.insert(tk.END, f"Paired T-Test: {col1} vs {col2}\n\n")
                
                elif test_type == "normality":
                    result = HypothesisTesting.normality_test(df[col1])
                    result_text.insert(tk.END, f"Normality Test: {col1}\n\n")
                
                else:
                    result_text.insert(tk.END, "Test not yet implemented in this interface\n")
                    return
                
                for key, value in result.items():
                    result_text.insert(tk.END, f"{key}: {value}\n")
                
                result_text.insert(tk.END, f"\n✅ {result.get('interpretation', '')}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Test failed: {str(e)}")
        
        ttk.Button(dialog, text="Run Test", command=run_test).pack(pady=10)
