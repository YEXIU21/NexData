"""
Cleaning Dialogs
Data cleaning dialog windows extracted from main_window.py
Follows separation of concerns and clean code principles
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import numpy as np


class CleaningDialogs:
    """Factory class for creating data cleaning dialog windows"""
    
    @staticmethod
    def show_remove_duplicates_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show remove duplicates dialog
        
        Args:
            parent: Parent window
            df: DataFrame to clean
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, removed_count, status_msg)
        """
        dialog = tk.Toplevel(parent)
        dialog.title("Remove Duplicates")
        dialog.geometry("500x450")
        
        ttk.Label(dialog, text="Remove Duplicate Rows", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Check for duplicates first
        all_duplicates = df.duplicated(keep=False).sum()
        ttk.Label(dialog, text=f"Found {all_duplicates} duplicate rows in dataset", 
                 font=('Arial', 10), foreground='red' if all_duplicates > 0 else 'green').pack(pady=5)
        
        # Column selection
        ttk.Label(dialog, text="Check duplicates based on:", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        col_frame = ttk.Frame(dialog)
        col_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Add scrollbar for column list
        scrollbar = ttk.Scrollbar(col_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox for column selection
        col_listbox = tk.Listbox(col_frame, selectmode=tk.MULTIPLE, 
                                yscrollcommand=scrollbar.set, height=8)
        col_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        scrollbar.config(command=col_listbox.yview)
        
        # Add all columns to listbox
        for col in df.columns:
            col_listbox.insert(tk.END, col)
        
        # Select all by default
        col_listbox.select_set(0, tk.END)
        
        ttk.Label(dialog, text="(Select columns to check - Ctrl+Click for multiple)", 
                 font=('Arial', 9), foreground='gray').pack()
        
        # Quick select buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def select_all():
            col_listbox.select_set(0, tk.END)
        
        def select_none():
            col_listbox.selection_clear(0, tk.END)
        
        ttk.Button(button_frame, text="Select All", command=select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", command=select_none).pack(side=tk.LEFT, padx=5)
        
        # Keep option
        ttk.Label(dialog, text="Which duplicate to keep:", 
                 font=('Arial', 10, 'bold')).pack(pady=(10,5))
        
        keep_var = tk.StringVar(value="first")
        ttk.Radiobutton(dialog, text="Keep first occurrence (recommended)", 
                       variable=keep_var, value="first").pack(pady=2)
        ttk.Radiobutton(dialog, text="Keep last occurrence", 
                       variable=keep_var, value="last").pack(pady=2)
        ttk.Radiobutton(dialog, text="Remove all duplicates (keep none)", 
                       variable=keep_var, value=False).pack(pady=2)
        
        # Action buttons
        action_frame = ttk.Frame(dialog)
        action_frame.pack(pady=20)
        
        def preview_duplicates():
            """Show which rows will be removed"""
            selected_indices = col_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Warning", "Please select at least one column!")
                return
            
            subset_cols = [col_listbox.get(i) for i in selected_indices]
            keep_option = keep_var.get()
            if keep_option == "False":
                keep_option = False
            
            # Find duplicates
            dup_mask = df.duplicated(subset=subset_cols, keep=keep_option)
            duplicates = df[dup_mask]
            
            if len(duplicates) == 0:
                messagebox.showinfo("Preview", "No duplicates found with selected columns!")
            else:
                preview_window = tk.Toplevel(dialog)
                preview_window.title("Duplicate Preview")
                preview_window.geometry("800x400")
                
                ttk.Label(preview_window, 
                         text=f"These {len(duplicates)} rows will be REMOVED:", 
                         font=('Arial', 11, 'bold'), foreground='red').pack(pady=10)
                
                text_widget = tk.Text(preview_window, wrap=tk.NONE)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                text_widget.insert(tk.END, duplicates.to_string())
                text_widget.config(state=tk.DISABLED)
        
        def remove():
            """Perform duplicate removal"""
            selected_indices = col_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Warning", "Please select at least one column!")
                return
            
            subset_cols = [col_listbox.get(i) for i in selected_indices]
            keep_option = keep_var.get()
            if keep_option == "False":
                keep_option = False
            
            try:
                # Use cleaning service
                cleaned_df, removed = cleaning_service.remove_duplicates(
                    df, 
                    subset=subset_cols, 
                    keep=keep_option
                )
                
                # Build status message
                status_msg = f"Removed {removed} duplicates"
                
                # Call callback with results
                on_complete_callback(cleaned_df, removed, status_msg, subset_cols, keep_option)
                
                # Show success message
                messagebox.showinfo("Success", 
                                  f"Removed {removed} duplicate rows\n\n"
                                  f"Based on columns: {', '.join(subset_cols)}\n"
                                  f"Keep strategy: {keep_option}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove duplicates: {str(e)}")
        
        ttk.Button(action_frame, text="Preview", command=preview_duplicates).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Remove Duplicates", command=remove, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_handle_missing_dialog(parent, df, on_complete_callback):
        """
        Show handle missing values dialog
        
        Args:
            parent: Parent window
            df: DataFrame to clean
            on_complete_callback: Callback function(cleaned_df, method, column, status_msg)
        """
        dialog = tk.Toplevel(parent)
        dialog.title("Handle Missing Values")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text=f"Total Missing Values: {df.isnull().sum().sum()}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Column selection
        ttk.Label(dialog, text="Select column (optional - leave for all):", 
                 font=('Arial', 10)).pack(pady=5)
        col_var = tk.StringVar(value="All Columns")
        cols_list = ["All Columns"] + list(df.columns)
        ttk.Combobox(dialog, textvariable=col_var, values=cols_list, 
                     state='readonly', width=40).pack(pady=5)
        
        # Method selection
        ttk.Label(dialog, text="Select method:", font=('Arial', 10, 'bold')).pack(pady=10)
        method_var = tk.StringVar(value="drop")
        ttk.Radiobutton(dialog, text="Drop rows with missing values", 
                       variable=method_var, value="drop").pack(pady=3)
        ttk.Radiobutton(dialog, text="Fill with mean (numeric only)", 
                       variable=method_var, value="mean").pack(pady=3)
        ttk.Radiobutton(dialog, text="Fill with median (numeric only)", 
                       variable=method_var, value="median").pack(pady=3)
        ttk.Radiobutton(dialog, text="Fill with custom value", 
                       variable=method_var, value="custom").pack(pady=3)
        ttk.Radiobutton(dialog, text="Forward fill", 
                       variable=method_var, value="ffill").pack(pady=3)
        
        # Custom value input
        ttk.Label(dialog, text="Custom value (if selected):", 
                 font=('Arial', 10)).pack(pady=5)
        custom_var = tk.StringVar(value="")
        ttk.Entry(dialog, textvariable=custom_var, width=30).pack(pady=5)
        
        def apply():
            method = method_var.get()
            selected_col = col_var.get()
            
            try:
                # Make a copy to modify
                result_df = df.copy()
                
                if selected_col == "All Columns":
                    # Apply to all columns
                    if method == "drop":
                        result_df = result_df.dropna()
                    elif method == "mean":
                        result_df.fillna(result_df.mean(numeric_only=True), inplace=True)
                    elif method == "median":
                        result_df.fillna(result_df.median(numeric_only=True), inplace=True)
                    elif method == "custom":
                        custom_val = custom_var.get()
                        if custom_val == "":
                            messagebox.showwarning("Warning", "Please enter a custom value!")
                            return
                        result_df.fillna(custom_val, inplace=True)
                    elif method == "ffill":
                        result_df.fillna(method='ffill', inplace=True)
                else:
                    # Apply to specific column
                    if method == "drop":
                        result_df = result_df.dropna(subset=[selected_col])
                    elif method == "mean":
                        if pd.api.types.is_numeric_dtype(result_df[selected_col]):
                            result_df[selected_col].fillna(result_df[selected_col].mean(), inplace=True)
                        else:
                            messagebox.showwarning("Warning", f"{selected_col} is not numeric!")
                            return
                    elif method == "median":
                        if pd.api.types.is_numeric_dtype(result_df[selected_col]):
                            result_df[selected_col].fillna(result_df[selected_col].median(), inplace=True)
                        else:
                            messagebox.showwarning("Warning", f"{selected_col} is not numeric!")
                            return
                    elif method == "custom":
                        custom_val = custom_var.get()
                        if custom_val == "":
                            messagebox.showwarning("Warning", "Please enter a custom value!")
                            return
                        result_df[selected_col].fillna(custom_val, inplace=True)
                    elif method == "ffill":
                        result_df[selected_col].fillna(method='ffill', inplace=True)
                
                # Build status message
                status_msg = f"Handled missing values: {method}"
                
                # Call callback
                on_complete_callback(result_df, method, selected_col, status_msg, custom_var.get() if method == "custom" else None)
                
                messagebox.showinfo("Success", f"Applied {method} method to {selected_col}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to handle missing values:\n{str(e)}")
        
        ttk.Button(dialog, text="Apply", command=apply).pack(pady=15)
    
    @staticmethod
    def show_remove_outliers_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show remove outliers dialog
        
        Args:
            parent: Parent window
            df: DataFrame to analyze
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, removed_count, status_msg, details)
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns found!")
            return
        
        # Create dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Remove Outliers")
        dialog.geometry("550x500")
        
        ttk.Label(dialog, text="Remove Outlier Detection & Removal", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Column selection
        ttk.Label(dialog, text="Select column to check for outliers:", 
                 font=('Arial', 10, 'bold')).pack(pady=(10,5))
        
        col_var = tk.StringVar(value=numeric_cols[0])
        col_dropdown = ttk.Combobox(dialog, textvariable=col_var, 
                                    values=numeric_cols, state='readonly', width=35)
        col_dropdown.pack(pady=5)
        
        # Method selection
        ttk.Label(dialog, text="Detection method:", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        method_var = tk.StringVar(value="iqr")
        ttk.Radiobutton(dialog, text="IQR Method (Interquartile Range) - Recommended", 
                       variable=method_var, value="iqr").pack(pady=2, anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Z-Score Method (Standard Deviation)", 
                       variable=method_var, value="zscore").pack(pady=2, anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Percentile Method (Custom range)", 
                       variable=method_var, value="percentile").pack(pady=2, anchor='w', padx=50)
        
        # Threshold settings
        threshold_frame = ttk.LabelFrame(dialog, text="Threshold Settings", padding=10)
        threshold_frame.pack(pady=15, padx=20, fill=tk.X)
        
        # IQR multiplier
        ttk.Label(threshold_frame, text="IQR Multiplier:").grid(row=0, column=0, sticky='w', pady=5)
        iqr_var = tk.DoubleVar(value=1.5)
        iqr_spin = ttk.Spinbox(threshold_frame, from_=0.5, to=5.0, increment=0.5, 
                               textvariable=iqr_var, width=10)
        iqr_spin.grid(row=0, column=1, padx=10)
        ttk.Label(threshold_frame, text="(Standard: 1.5, Strict: 3.0)", 
                 font=('Arial', 8), foreground='gray').grid(row=0, column=2, sticky='w')
        
        # Z-Score threshold
        ttk.Label(threshold_frame, text="Z-Score Threshold:").grid(row=1, column=0, sticky='w', pady=5)
        zscore_var = tk.DoubleVar(value=3.0)
        zscore_spin = ttk.Spinbox(threshold_frame, from_=1.0, to=5.0, increment=0.5, 
                                  textvariable=zscore_var, width=10)
        zscore_spin.grid(row=1, column=1, padx=10)
        ttk.Label(threshold_frame, text="(Standard: 3.0, Strict: 2.5)", 
                 font=('Arial', 8), foreground='gray').grid(row=1, column=2, sticky='w')
        
        # Percentile range
        ttk.Label(threshold_frame, text="Keep Percentile Range:").grid(row=2, column=0, sticky='w', pady=5)
        perc_frame = ttk.Frame(threshold_frame)
        perc_frame.grid(row=2, column=1, columnspan=2, sticky='w', padx=10)
        perc_low_var = tk.DoubleVar(value=1.0)
        perc_high_var = tk.DoubleVar(value=99.0)
        ttk.Spinbox(perc_frame, from_=0.0, to=50.0, increment=1.0, 
                   textvariable=perc_low_var, width=8).pack(side=tk.LEFT)
        ttk.Label(perc_frame, text=" to ").pack(side=tk.LEFT)
        ttk.Spinbox(perc_frame, from_=50.0, to=100.0, increment=1.0, 
                   textvariable=perc_high_var, width=8).pack(side=tk.LEFT)
        
        # Results display
        result_text = tk.Text(dialog, height=6, width=60, wrap=tk.WORD)
        result_text.pack(pady=10, padx=20)
        result_text.config(state=tk.DISABLED)
        
        def detect_outliers():
            """Detect and show outliers without removing"""
            col = col_var.get()
            method = method_var.get()
            
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            
            try:
                if method == "iqr":
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    multiplier = iqr_var.get()
                    lower_bound = Q1 - multiplier * IQR
                    upper_bound = Q3 + multiplier * IQR
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    
                    result_text.insert(tk.END, f"📊 IQR Method (Multiplier: {multiplier})\n")
                    result_text.insert(tk.END, f"Q1: {Q1:.2f}, Q3: {Q3:.2f}, IQR: {IQR:.2f}\n")
                    result_text.insert(tk.END, f"Valid range: {lower_bound:.2f} to {upper_bound:.2f}\n")
                    
                elif method == "zscore":
                    from scipy import stats
                    threshold = zscore_var.get()
                    z_scores = np.abs(stats.zscore(df[col].dropna()))
                    outliers = df[np.abs(stats.zscore(df[col])) > threshold]
                    
                    result_text.insert(tk.END, f"📊 Z-Score Method (Threshold: {threshold})\n")
                    result_text.insert(tk.END, f"Mean: {df[col].mean():.2f}, Std: {df[col].std():.2f}\n")
                    
                elif method == "percentile":
                    low_perc = perc_low_var.get()
                    high_perc = perc_high_var.get()
                    lower_bound = df[col].quantile(low_perc / 100)
                    upper_bound = df[col].quantile(high_perc / 100)
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    
                    result_text.insert(tk.END, f"📊 Percentile Method ({low_perc}% - {high_perc}%)\n")
                    result_text.insert(tk.END, f"Valid range: {lower_bound:.2f} to {upper_bound:.2f}\n")
                
                result_text.insert(tk.END, f"\n🎯 Found {len(outliers)} outlier rows\n")
                if len(outliers) > 0:
                    result_text.insert(tk.END, f"Outlier values: {outliers[col].tolist()[:10]}\n")
                    if len(outliers) > 10:
                        result_text.insert(tk.END, f"... and {len(outliers)-10} more")
                
            except Exception as e:
                result_text.insert(tk.END, f"❌ Error: {str(e)}")
            
            result_text.config(state=tk.DISABLED)
        
        def remove():
            """Remove detected outliers"""
            col = col_var.get()
            method = method_var.get()
            
            try:
                # Get threshold based on method
                if method == "iqr":
                    threshold = iqr_var.get()
                elif method == "zscore":
                    threshold = zscore_var.get()
                else:  # percentile method not supported in service yet, use IQR as fallback
                    method = "iqr"
                    threshold = 1.5
                
                # Use cleaning service
                cleaned_df, removed = cleaning_service.remove_outliers(
                    df,
                    col,
                    method=method,
                    threshold=threshold
                )
                
                # Build status message
                status_msg = f"Removed {removed} outliers"
                details = {
                    'column': col,
                    'method': method.upper(),
                    'threshold': threshold
                }
                
                # Call callback with results
                on_complete_callback(cleaned_df, removed, status_msg, details)
                
                messagebox.showinfo("Success", 
                                  f"Removed {removed} outlier rows\n\n"
                                  f"Column: {col}\n"
                                  f"Method: {method.upper()}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove outliers:\n{str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Detect Outliers", 
                  command=detect_outliers).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Outliers", command=remove, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
