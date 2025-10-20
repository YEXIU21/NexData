"""
Analysis Dialog Classes
Contains all analysis-related dialogs extracted from main_window.py
Following SEPARATION OF CONCERNS and CLEAN CODE principles
"""

import tkinter as tk
from tkinter import ttk, messagebox
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
