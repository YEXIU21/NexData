"""
Data Cleaning Dialog Classes
Contains all cleaning-related dialogs extracted from main_window.py
Following SEPARATION OF CONCERNS and CLEAN CODE principles
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import re
from datetime import datetime

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
    
    @staticmethod
    def show_smart_fill_missing_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show smart fill missing values dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, filled_count, status_msg, details)
        """
        # Find columns with missing values
        missing_cols = df.columns[df.isnull().any()].tolist()
        if not missing_cols:
            messagebox.showinfo("Info", "No missing values found in the dataset!")
            return
        
        # Create dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Smart Fill Missing Data")
        dialog.geometry("650x600")
        
        ttk.Label(dialog, text="Smart Fill Missing Data - Intelligent Lookup", 
                 font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Instructions
        info_frame = ttk.LabelFrame(dialog, text="How It Works", padding=10)
        info_frame.pack(pady=10, padx=20, fill=tk.X)
        ttk.Label(info_frame, text="• Select column with missing values (e.g., customer_name)\n"
                                   "• Select lookup key column (e.g., customer_id)\n"
                                   "• System finds matching rows and fills missing values\n"
                                   "• Preview shows what will be filled",
                 justify=tk.LEFT).pack()
        
        # Column with missing values
        ttk.Label(dialog, text="Column with missing values:", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        target_col_var = tk.StringVar()
        target_col_dropdown = ttk.Combobox(dialog, textvariable=target_col_var,
                                          values=missing_cols, state='readonly', width=25)
        target_col_dropdown.pack(pady=5)
        if missing_cols:
            target_col_dropdown.current(0)
        
        # Lookup key column
        ttk.Label(dialog, text="Lookup key column (ID to match on):", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        key_col_var = tk.StringVar()
        all_cols = list(df.columns)
        key_col_dropdown = ttk.Combobox(dialog, textvariable=key_col_var,
                                       values=all_cols, state='readonly', width=25)
        key_col_dropdown.pack(pady=5)
        # Try to auto-detect ID column
        id_cols = [col for col in all_cols if 'id' in col.lower()]
        if id_cols:
            key_col_var.set(id_cols[0])
        elif all_cols:
            key_col_dropdown.current(0)
        
        # Preview area
        preview_frame = ttk.LabelFrame(dialog, text="Preview - What Will Be Filled", padding=10)
        preview_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)
        
        preview_text = tk.Text(preview_frame, height=15, width=70, wrap=tk.NONE)
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
        preview_text.config(yscrollcommand=preview_scroll.set)
        preview_text.grid(row=0, column=0, sticky='nsew')
        preview_scroll.grid(row=0, column=1, sticky='ns')
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            """Preview what will be filled"""
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            target_col = target_col_var.get()
            key_col = key_col_var.get()
            
            if not target_col or not key_col:
                preview_text.insert(tk.END, "⚠️ Please select both columns\n")
                preview_text.config(state=tk.DISABLED)
                return
            
            try:
                # Find rows with missing values in target column
                missing_mask = df[target_col].isnull()
                missing_rows = df[missing_mask]
                
                if len(missing_rows) == 0:
                    preview_text.insert(tk.END, f"✓ No missing values in '{target_col}'\n")
                    preview_text.config(state=tk.DISABLED)
                    return
                
                # For each missing row, find matching rows and get fill value
                fill_preview = []
                for idx, row in missing_rows.iterrows():
                    key_value = row[key_col]
                    
                    # Find matching rows with same key that have non-null target value
                    matches = df[(df[key_col] == key_value) & 
                                     (df[target_col].notnull())]
                    
                    if len(matches) > 0:
                        # Get most common value
                        fill_value = matches[target_col].mode()[0] if len(matches[target_col].mode()) > 0 else matches[target_col].iloc[0]
                        fill_preview.append({
                            'index': idx,
                            'key': key_value,
                            'fill_value': fill_value,
                            'found_in': len(matches)
                        })
                
                if not fill_preview:
                    preview_text.insert(tk.END, f"⚠️ No matching rows found to fill missing values\n\n")
                    preview_text.insert(tk.END, f"Missing {target_col}: {len(missing_rows)} rows\n")
                    preview_text.insert(tk.END, f"But no other rows with same {key_col} have valid {target_col}\n")
                else:
                    preview_text.insert(tk.END, f"📋 Can fill {len(fill_preview)} of {len(missing_rows)} missing values:\n\n")
                    preview_text.insert(tk.END, f"{'Row':<6} {key_col:<15} → {target_col}\n")
                    preview_text.insert(tk.END, "=" * 60 + "\n")
                    
                    for item in fill_preview[:15]:
                        preview_text.insert(tk.END, 
                            f"{item['index']:<6} {str(item['key']):<15} → {item['fill_value']} "
                            f"(from {item['found_in']} matches)\n")
                    
                    if len(fill_preview) > 15:
                        preview_text.insert(tk.END, f"\n... and {len(fill_preview) - 15} more\n")
                    
                    unfillable = len(missing_rows) - len(fill_preview)
                    if unfillable > 0:
                        preview_text.insert(tk.END, f"\n⚠️ {unfillable} rows cannot be filled (no matching {key_col})\n")
                
            except Exception as e:
                preview_text.insert(tk.END, f"❌ Error: {str(e)}")
            
            preview_text.config(state=tk.DISABLED)
        
        def apply_fill():
            """Apply the smart fill"""
            target_col = target_col_var.get()
            key_col = key_col_var.get()
            
            if not target_col or not key_col:
                messagebox.showwarning("Warning", "Please select both columns!")
                return
            
            try:
                # Find rows with missing values
                missing_mask = df[target_col].isnull()
                missing_rows = df[missing_mask]
                before_count = len(missing_rows)
                
                # Use cleaning service
                cleaned_df, filled_count = cleaning_service.smart_fill_missing(
                    df,
                    target_col,
                    key_col
                )
                
                # Build status message
                status_msg = f"Smart filled {filled_count} values"
                details = {
                    'target_column': target_col,
                    'lookup_key': key_col,
                    'filled': filled_count,
                    'before': before_count,
                    'still_missing': before_count - filled_count
                }
                
                # Call callback with results
                on_complete_callback(cleaned_df, filled_count, status_msg, details)
                
                messagebox.showinfo("Success", 
                                  f"Smart fill complete!\n\n"
                                  f"Filled: {filled_count} values\n"
                                  f"Still missing: {before_count - filled_count}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fill missing data:\n{str(e)}")
        
        # Action buttons
        action_frame = ttk.Frame(dialog)
        action_frame.pack(pady=15)
        
        ttk.Button(action_frame, text="Preview", command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Apply Fill", command=apply_fill, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_find_replace_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show find and replace dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, count, status_msg, details)
        """
        import tkinter.scrolledtext as scrolledtext
        
        dialog = tk.Toplevel(parent)
        dialog.title("Find & Replace")
        dialog.geometry("550x450")
        
        ttk.Label(dialog, text="Find & Replace Values", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Scope selection
        ttk.Label(dialog, text="Search in:", font=('Arial', 10, 'bold')).pack(pady=(10,5))
        scope_var = tk.StringVar(value="all")
        ttk.Radiobutton(dialog, text="All columns", variable=scope_var, value="all").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Specific column", variable=scope_var, value="specific").pack(anchor='w', padx=50)
        
        col_var = tk.StringVar()
        col_dropdown = ttk.Combobox(dialog, textvariable=col_var, values=list(df.columns), state='readonly', width=25)
        col_dropdown.pack(pady=5)
        if len(df.columns) > 0:
            col_dropdown.current(0)
        
        # Find and replace inputs
        ttk.Label(dialog, text="Find what:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        find_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=find_var, width=40).pack(pady=5)
        
        ttk.Label(dialog, text="Replace with:", font=('Arial', 10, 'bold')).pack(pady=(10,5))
        replace_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=replace_var, width=40).pack(pady=5)
        
        case_sensitive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Case sensitive", variable=case_sensitive_var).pack(pady=5)
        
        # Preview area
        preview_text = scrolledtext.ScrolledText(dialog, height=6, width=60)
        preview_text.pack(pady=10, padx=20)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            find_val = find_var.get()
            if not find_val:
                messagebox.showwarning("Warning", "Please enter a value to find!")
                return
                
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                count = 0
                if scope_var.get() == "all":
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            matches = df[col].astype(str).str.contains(find_val, case=case_sensitive_var.get(), na=False).sum()
                            count += matches
                else:
                    col = col_var.get()
                    count = df[col].astype(str).str.contains(find_val, case=case_sensitive_var.get(), na=False).sum()
                    
                preview_text.insert(tk.END, f"Found '{find_val}' in {count} cell(s)\n")
                preview_text.insert(tk.END, f"Will replace with '{replace_var.get()}'\n")
            except Exception as e:
                preview_text.insert(tk.END, f"Error: {str(e)}")
                
            preview_text.config(state=tk.DISABLED)
        
        def apply_replace():
            find_val = find_var.get()
            replace_val = replace_var.get()
            
            if not find_val:
                messagebox.showwarning("Warning", "Please enter a value to find!")
                return
            
            try:
                count = 0
                result_df = df.copy()
                
                if scope_var.get() == "all":
                    # Apply to all text columns
                    for col in result_df.columns:
                        if result_df[col].dtype == 'object':
                            result_df, num_replaced = cleaning_service.find_and_replace(
                                result_df, col, find_val, replace_val, exact_match=not case_sensitive_var.get()
                            )
                            count += 1
                else:
                    # Apply to specific column
                    col = col_var.get()
                    result_df, num_replaced = cleaning_service.find_and_replace(
                        result_df, col, find_val, replace_val, exact_match=not case_sensitive_var.get()
                    )
                    count = 1
                
                # Build status message
                status_msg = f"Replaced '{find_val}' with '{replace_val}'"
                details = {
                    'find': find_val,
                    'replace': replace_val,
                    'scope': scope_var.get(),
                    'column': col_var.get() if scope_var.get() == "specific" else "all",
                    'count': count
                }
                
                # Call callback
                on_complete_callback(result_df, count, status_msg, details)
                
                messagebox.showinfo("Success", f"Replace complete!\nProcessed {count} column(s)")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Replace failed:\n{str(e)}")
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Preview", command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Replace All", command=apply_replace, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_standardize_text_case_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show standardize text case dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, col, case, status_msg)
        """
        import tkinter.scrolledtext as scrolledtext
        import pandas as pd
        
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not text_cols:
            messagebox.showinfo("Info", "No text columns found!")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Standardize Text Case")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Standardize Text Case", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Column selection
        ttk.Label(dialog, text="Select column:", font=('Arial', 10, 'bold')).pack(pady=(10,5))
        col_var = tk.StringVar()
        col_dropdown = ttk.Combobox(dialog, textvariable=col_var, values=text_cols, state='readonly', width=25)
        col_dropdown.pack(pady=5)
        if text_cols:
            col_dropdown.current(0)
        
        # Case selection
        ttk.Label(dialog, text="Convert to:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        case_var = tk.StringVar(value="title")
        ttk.Radiobutton(dialog, text="Title Case (John Smith)", variable=case_var, value="title").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="UPPERCASE (JOHN SMITH)", variable=case_var, value="upper").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="lowercase (john smith)", variable=case_var, value="lower").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Sentence case (John smith)", variable=case_var, value="sentence").pack(anchor='w', padx=50)
        
        # Preview area
        preview_text = scrolledtext.ScrolledText(dialog, height=6, width=50)
        preview_text.pack(pady=10, padx=20)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            col = col_var.get()
            case = case_var.get()
            
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                sample = df[col].head(5)
                preview_text.insert(tk.END, "Preview (first 5 values):\n\n")
                for val in sample:
                    if pd.notna(val):
                        if case == "title":
                            new_val = str(val).title()
                        elif case == "upper":
                            new_val = str(val).upper()
                        elif case == "lower":
                            new_val = str(val).lower()
                        else:  # sentence
                            new_val = str(val).capitalize()
                        preview_text.insert(tk.END, f"{val} → {new_val}\n")
            except Exception as e:
                preview_text.insert(tk.END, f"Error: {str(e)}")
                
            preview_text.config(state=tk.DISABLED)
        
        def apply_case():
            col = col_var.get()
            case = case_var.get()
            
            try:
                # Map UI case names to service case names
                case_mapping = {
                    "sentence": "capitalize"
                }
                service_case = case_mapping.get(case, case)
                
                # Use cleaning service
                cleaned_df = cleaning_service.standardize_text_case(
                    df, 
                    [col], 
                    service_case
                )
                
                # Build status message
                status_msg = f"Standardized {col} to {case} case"
                
                # Call callback
                on_complete_callback(cleaned_df, col, case, status_msg)
                
                messagebox.showinfo("Success", f"Text case standardized for '{col}'!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to standardize case: {str(e)}")
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Preview", command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Apply", command=apply_case, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_remove_empty_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show remove empty rows/columns dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, rows_removed, cols_removed, status_msg)
        """
        import tkinter.scrolledtext as scrolledtext
        
        dialog = tk.Toplevel(parent)
        dialog.title("Remove Empty Rows/Columns")
        dialog.geometry("450x350")
        
        ttk.Label(dialog, text="Remove Empty Rows/Columns", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Calculate empty rows and columns
        empty_rows = df.isnull().all(axis=1).sum()
        empty_cols = df.isnull().all(axis=0).sum()
        
        # Info display
        info_text = scrolledtext.ScrolledText(dialog, height=10, width=50)
        info_text.pack(pady=10, padx=20)
        info_text.insert(tk.END, f"Dataset Analysis:\n\n")
        info_text.insert(tk.END, f"Total rows: {len(df)}\n")
        info_text.insert(tk.END, f"Total columns: {len(df.columns)}\n\n")
        info_text.insert(tk.END, f"Empty rows: {empty_rows}\n")
        info_text.insert(tk.END, f"Empty columns: {empty_cols}\n")
        info_text.config(state=tk.DISABLED)
        
        # Options
        remove_rows_var = tk.BooleanVar(value=True)
        remove_cols_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text=f"Remove {empty_rows} empty row(s)", 
                       variable=remove_rows_var).pack(pady=5)
        ttk.Checkbutton(dialog, text=f"Remove {empty_cols} empty column(s)", 
                       variable=remove_cols_var).pack(pady=5)
        
        def apply_remove():
            try:
                # Use cleaning service
                cleaned_df, rows_removed, cols_removed = cleaning_service.remove_empty_rows_columns(
                    df,
                    remove_rows=remove_rows_var.get(),
                    remove_cols=remove_cols_var.get()
                )
                
                # Build status message
                status_msg = f"Removed {rows_removed} rows, {cols_removed} columns"
                
                # Call callback
                on_complete_callback(cleaned_df, rows_removed, cols_removed, status_msg)
                
                messagebox.showinfo("Success", 
                                  f"Removed:\n{rows_removed} empty row(s)\n{cols_removed} empty column(s)")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove empty rows/columns: {str(e)}")
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Remove", command=apply_remove, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_convert_data_types_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show convert data types dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, col, target_type, status_msg)
        """
        import tkinter.scrolledtext as scrolledtext
        import pandas as pd
        
        dialog = tk.Toplevel(parent)
        dialog.title("Convert Data Types")
        dialog.geometry("500x450")
        
        ttk.Label(dialog, text="Convert Data Types", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Column selection
        ttk.Label(dialog, text="Select column:", font=('Arial', 10, 'bold')).pack(pady=5)
        col_var = tk.StringVar()
        col_combo = ttk.Combobox(dialog, textvariable=col_var, values=list(df.columns), state='readonly', width=25)
        col_combo.pack(pady=5)
        if len(df.columns) > 0:
            col_combo.current(0)
        
        # Current type display
        current_type_label = ttk.Label(dialog, text="", font=('Arial', 9))
        current_type_label.pack(pady=5)
        
        def update_type(*args):
            if col_var.get():
                current_type_label.config(text=f"Current type: {df[col_var.get()].dtype}")
        
        col_var.trace('w', update_type)
        
        # Target type selection
        ttk.Label(dialog, text="Convert to:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        type_var = tk.StringVar(value="number")
        ttk.Radiobutton(dialog, text="Number (int/float)", variable=type_var, value="number").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Text (string)", variable=type_var, value="text").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Date/Time", variable=type_var, value="datetime").pack(anchor='w', padx=50)
        
        # Error handling
        ttk.Label(dialog, text="Handle errors:", font=('Arial', 9)).pack(pady=(10,5))
        errors_var = tk.StringVar(value="coerce")
        ttk.Radiobutton(dialog, text="Convert to NaN (recommended)", variable=errors_var, value="coerce").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Keep original value", variable=errors_var, value="ignore").pack(anchor='w', padx=50)
        
        # Preview area
        preview_text = scrolledtext.ScrolledText(dialog, height=6, width=50)
        preview_text.pack(pady=10, padx=20)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            col = col_var.get()
            target_type = type_var.get()
            
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                sample = df[col].head(5)
                preview_text.insert(tk.END, "Preview (first 5 values):\n\n")
                for val in sample:
                    if pd.notna(val):
                        try:
                            if target_type == "number":
                                new_val = pd.to_numeric(val, errors=errors_var.get())
                            elif target_type == "text":
                                new_val = str(val)
                            else:  # datetime
                                new_val = pd.to_datetime(val, errors=errors_var.get())
                            preview_text.insert(tk.END, f"{val} → {new_val}\n")
                        except:
                            preview_text.insert(tk.END, f"{val} → [conversion error]\n")
            except Exception as e:
                preview_text.insert(tk.END, f"Error: {str(e)}")
                
            preview_text.config(state=tk.DISABLED)
        
        def apply_conversion():
            col = col_var.get()
            target_type = type_var.get()
            
            try:
                # Map UI type names to service type names
                type_mapping = {
                    "number": "float",
                    "text": "string",
                    "datetime": "datetime"
                }
                service_type = type_mapping.get(target_type, target_type)
                
                # Use cleaning service
                cleaned_df = cleaning_service.convert_data_types(
                    df, 
                    col, 
                    service_type
                )
                
                # Build status message
                status_msg = f"Converted {col} to {target_type}"
                
                # Call callback
                on_complete_callback(cleaned_df, col, target_type, status_msg)
                
                messagebox.showinfo("Success", f"'{col}' converted to {target_type}!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Preview", command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Convert", command=apply_conversion, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_standardize_dates_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show standardize dates dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, col, fmt, status_msg)
        """
        import tkinter.scrolledtext as scrolledtext
        import pandas as pd
        
        dialog = tk.Toplevel(parent)
        dialog.title("Standardize Dates")
        dialog.geometry("500x450")
        
        ttk.Label(dialog, text="Standardize Date Format", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Column selection
        ttk.Label(dialog, text="Select date column:", font=('Arial', 10, 'bold')).pack(pady=5)
        col_var = tk.StringVar()
        col_combo = ttk.Combobox(dialog, textvariable=col_var, values=list(df.columns), state='readonly', width=25)
        col_combo.pack(pady=5)
        if len(df.columns) > 0:
            col_combo.current(0)
        
        # Format selection
        ttk.Label(dialog, text="Target format:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        format_var = tk.StringVar(value="%Y-%m-%d")
        ttk.Radiobutton(dialog, text="YYYY-MM-DD (2025-01-05)", variable=format_var, value="%Y-%m-%d").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="MM/DD/YYYY (01/05/2025)", variable=format_var, value="%m/%d/%Y").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="DD/MM/YYYY (05/01/2025)", variable=format_var, value="%d/%m/%Y").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Month DD, YYYY (January 05, 2025)", variable=format_var, value="%B %d, %Y").pack(anchor='w', padx=50)
        
        # Preview area
        preview_text = scrolledtext.ScrolledText(dialog, height=8, width=55)
        preview_text.pack(pady=10, padx=20)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            col = col_var.get()
            fmt = format_var.get()
            
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                sample = pd.to_datetime(df[col], errors='coerce').head(5)
                preview_text.insert(tk.END, "Preview (first 5 values):\n\n")
                for val in sample:
                    if pd.notna(val):
                        preview_text.insert(tk.END, f"{val} → {val.strftime(fmt)}\n")
                    else:
                        preview_text.insert(tk.END, "[invalid date]\n")
            except Exception as e:
                preview_text.insert(tk.END, f"Error: {str(e)}")
                
            preview_text.config(state=tk.DISABLED)
        
        def apply_format():
            col = col_var.get()
            fmt = format_var.get()
            
            try:
                # Use cleaning service
                cleaned_df = cleaning_service.standardize_dates(
                    df,
                    col,
                    date_format=fmt
                )
                
                # Build status message
                status_msg = f"Standardized dates in {col}"
                
                # Call callback
                on_complete_callback(cleaned_df, col, fmt, status_msg)
                
                messagebox.showinfo("Success", f"Dates in '{col}' standardized to {fmt}!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to standardize dates: {str(e)}")
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Preview", command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Apply", command=apply_format, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_remove_special_chars_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show remove special characters dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, col, status_msg)
        """
        import tkinter.scrolledtext as scrolledtext
        import pandas as pd
        import re
        
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not text_cols:
            messagebox.showinfo("Info", "No text columns found!")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Remove Special Characters")
        dialog.geometry("500x450")
        
        ttk.Label(dialog, text="Remove Special Characters", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Column selection
        ttk.Label(dialog, text="Select column:", font=('Arial', 10, 'bold')).pack(pady=5)
        col_var = tk.StringVar()
        col_combo = ttk.Combobox(dialog, textvariable=col_var, values=text_cols, state='readonly', width=25)
        col_combo.pack(pady=5)
        if text_cols:
            col_combo.current(0)
        
        # Mode selection
        ttk.Label(dialog, text="Remove:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        mode_var = tk.StringVar(value="all")
        ttk.Radiobutton(dialog, text="All special characters (!@#$%^&*)", variable=mode_var, value="all").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Punctuation only (.,!?;:)", variable=mode_var, value="punct").pack(anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Custom characters", variable=mode_var, value="custom").pack(anchor='w', padx=50)
        
        ttk.Label(dialog, text="Custom characters to remove:", font=('Arial', 9)).pack(pady=(10,5))
        custom_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=custom_var, width=30).pack(pady=5)
        
        # Preview area
        preview_text = scrolledtext.ScrolledText(dialog, height=6, width=50)
        preview_text.pack(pady=10, padx=20)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            col = col_var.get()
            mode = mode_var.get()
            
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                sample = df[col].head(5)
                preview_text.insert(tk.END, "Preview (first 5 values):\n\n")
                for val in sample:
                    if pd.notna(val):
                        if mode == "all":
                            new_val = re.sub(r'[^a-zA-Z0-9\s]', '', str(val))
                        elif mode == "punct":
                            new_val = re.sub(r'[.,!?;:]', '', str(val))
                        else:
                            chars = custom_var.get()
                            new_val = str(val)
                            for char in chars:
                                new_val = new_val.replace(char, '')
                        preview_text.insert(tk.END, f"{val} → {new_val}\n")
            except Exception as e:
                preview_text.insert(tk.END, f"Error: {str(e)}")
                
            preview_text.config(state=tk.DISABLED)
        
        def apply_remove():
            col = col_var.get()
            mode = mode_var.get()
            
            try:
                # Determine keep_alphanumeric based on mode
                if mode == "all":
                    keep_alphanumeric = True
                    custom_chars = None
                elif mode == "punct":
                    keep_alphanumeric = False
                    custom_chars = ".,!?;:"
                else:
                    keep_alphanumeric = False
                    custom_chars = custom_var.get()
                
                # Use cleaning service
                cleaned_df = cleaning_service.remove_special_characters(
                    df,
                    col,
                    keep_alphanumeric=keep_alphanumeric,
                    custom_chars=custom_chars
                )
                
                # Build status message
                status_msg = f"Removed special characters from {col}"
                
                # Call callback
                on_complete_callback(cleaned_df, col, status_msg)
                
                messagebox.showinfo("Success", f"Special characters removed from '{col}'!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove special characters: {str(e)}")
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Preview", command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Apply", command=apply_remove, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_split_column_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show split column dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, col, num_cols, status_msg)
        """
        import tkinter.scrolledtext as scrolledtext
        import pandas as pd
        
        dialog = tk.Toplevel(parent)
        dialog.title("Split Column")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Split Column by Delimiter", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Column selection
        ttk.Label(dialog, text="Select column to split:", font=('Arial', 10, 'bold')).pack(pady=5)
        col_var = tk.StringVar()
        col_combo = ttk.Combobox(dialog, textvariable=col_var, values=list(df.columns), state='readonly', width=25)
        col_combo.pack(pady=5)
        if len(df.columns) > 0:
            col_combo.current(0)
        
        # Delimiter selection
        ttk.Label(dialog, text="Delimiter:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        delimiter_var = tk.StringVar(value=" ")
        delimiter_frame = ttk.Frame(dialog)
        delimiter_frame.pack(pady=5)
        ttk.Radiobutton(delimiter_frame, text="Space", variable=delimiter_var, value=" ").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(delimiter_frame, text="Comma", variable=delimiter_var, value=",").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(delimiter_frame, text="Hyphen", variable=delimiter_var, value="-").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dialog, text="Custom:", font=('Arial', 9)).pack(pady=5)
        custom_delim = tk.StringVar()
        ttk.Entry(dialog, textvariable=custom_delim, width=10).pack(pady=5)
        
        # Preview area
        preview_text = scrolledtext.ScrolledText(dialog, height=6, width=50)
        preview_text.pack(pady=10, padx=20)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            col = col_var.get()
            delim = custom_delim.get() if custom_delim.get() else delimiter_var.get()
            
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                sample = df[col].head(3)
                preview_text.insert(tk.END, f"Preview (delimiter: '{delim}'):\n\n")
                for val in sample:
                    if pd.notna(val):
                        parts = str(val).split(delim)
                        preview_text.insert(tk.END, f"{val} → {len(parts)} parts: {parts}\n")
            except Exception as e:
                preview_text.insert(tk.END, f"Error: {str(e)}")
                
            preview_text.config(state=tk.DISABLED)
        
        def apply_split():
            col = col_var.get()
            delim = custom_delim.get() if custom_delim.get() else delimiter_var.get()
            
            try:
                # Use cleaning service
                cleaned_df, num_cols = cleaning_service.split_column(
                    df,
                    col,
                    delimiter=delim
                )
                
                # Build status message
                status_msg = f"Split {col} into {num_cols} columns"
                
                # Call callback
                on_complete_callback(cleaned_df, col, num_cols, status_msg)
                
                messagebox.showinfo("Success", f"Split '{col}' into {num_cols} columns!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to split column:\n{str(e)}")
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Preview", command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Split", command=apply_split, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_merge_columns_dialog(parent, df, cleaning_service, on_complete_callback):
        """
        Show merge columns dialog
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, col1, col2, new_name, status_msg)
        """
        import tkinter.scrolledtext as scrolledtext
        
        dialog = tk.Toplevel(parent)
        dialog.title("Merge Columns")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Merge Multiple Columns", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Column selection
        ttk.Label(dialog, text="Select first column:", font=('Arial', 10, 'bold')).pack(pady=5)
        col1_var = tk.StringVar()
        col1_combo = ttk.Combobox(dialog, textvariable=col1_var, values=list(df.columns), state='readonly', width=25)
        col1_combo.pack(pady=5)
        if len(df.columns) > 0:
            col1_combo.current(0)
        
        ttk.Label(dialog, text="Select second column:", font=('Arial', 10, 'bold')).pack(pady=5)
        col2_var = tk.StringVar()
        col2_combo = ttk.Combobox(dialog, textvariable=col2_var, values=list(df.columns), state='readonly', width=25)
        col2_combo.pack(pady=5)
        if len(df.columns) > 1:
            col2_combo.current(1)
        
        # Separator selection
        ttk.Label(dialog, text="Separator:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        sep_var = tk.StringVar(value=" ")
        sep_frame = ttk.Frame(dialog)
        sep_frame.pack(pady=5)
        ttk.Radiobutton(sep_frame, text="Space", variable=sep_var, value=" ").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sep_frame, text="Comma", variable=sep_var, value=",").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sep_frame, text="None", variable=sep_var, value="").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dialog, text="New column name:", font=('Arial', 9)).pack(pady=5)
        new_name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=new_name_var, width=30).pack(pady=5)
        
        # Preview area
        preview_text = scrolledtext.ScrolledText(dialog, height=6, width=50)
        preview_text.pack(pady=10, padx=20)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            col1 = col1_var.get()
            col2 = col2_var.get()
            sep = sep_var.get()
            
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                preview_text.insert(tk.END, f"Preview (separator: '{sep}'):\n\n")
                for i in range(min(3, len(df))):
                    val1 = str(df[col1].iloc[i])
                    val2 = str(df[col2].iloc[i])
                    merged = val1 + sep + val2
                    preview_text.insert(tk.END, f"{val1} + {val2} → {merged}\n")
            except Exception as e:
                preview_text.insert(tk.END, f"Error: {str(e)}")
                
            preview_text.config(state=tk.DISABLED)
        
        def apply_merge():
            col1 = col1_var.get()
            col2 = col2_var.get()
            sep = sep_var.get()
            new_name = new_name_var.get() if new_name_var.get() else f"{col1}_{col2}"
            
            try:
                # Use cleaning service
                cleaned_df = cleaning_service.merge_columns(
                    df,
                    [col1, col2],
                    separator=sep,
                    new_column_name=new_name
                )
                
                # Build status message
                status_msg = f"Merged {col1} and {col2}"
                
                # Call callback
                on_complete_callback(cleaned_df, col1, col2, new_name, status_msg)
                
                messagebox.showinfo("Success", f"Merged '{col1}' and '{col2}' into '{new_name}'!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to merge columns:\n{str(e)}")
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Preview", command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Merge", command=apply_merge, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_clean_order_ids_dialog(parent, df, on_complete_callback):
        """
        Show clean order IDs dialog - removes letter suffixes, whitespace, etc.
        
        Args:
            parent: Parent window
            df: DataFrame to process
            on_complete_callback: Callback function(cleaned_df, col, affected_count, status_msg, output_msg)
        """
        import re
        
        # Create dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Clean Order IDs")
        dialog.geometry("600x550")
        
        ttk.Label(dialog, text="Clean Order IDs - Remove Letter Suffixes", 
                 font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Instructions
        info_frame = ttk.LabelFrame(dialog, text="What This Does", padding=10)
        info_frame.pack(pady=10, padx=20, fill=tk.X)
        ttk.Label(info_frame, text="• Removes letter suffixes from Order IDs (e.g., SH10031B → SH10031)\n"
                                   "• Useful for cleaning test orders or accidental letter additions\n"
                                   "• Preserves the base ID number",
                 justify=tk.LEFT).pack()
        
        # Column selection
        ttk.Label(dialog, text="Select Order ID column:", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        col_var = tk.StringVar()
        # Try to auto-detect order_id column
        order_cols = [col for col in df.columns if 'id' in col.lower() and 'order' in col.lower()]
        if order_cols:
            col_var.set(order_cols[0])
        elif len(df.columns) > 0:
            col_var.set(df.columns[0])
        
        col_dropdown = ttk.Combobox(dialog, textvariable=col_var, 
                                    values=list(df.columns), state='readonly', width=35)
        col_dropdown.pack(pady=5)
        
        # Pattern options
        ttk.Label(dialog, text="Cleaning pattern:", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        pattern_var = tk.StringVar(value="all_letters")
        ttk.Radiobutton(dialog, text="Remove all letters at end (e.g., SH10031B → SH10031)", 
                       variable=pattern_var, value="all_letters").pack(pady=2, anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Remove single letter only (e.g., SH10031B → SH10031, but keep SH10ABC)", 
                       variable=pattern_var, value="single_letter").pack(pady=2, anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Remove numbers at end (e.g., SH10031B1 → SH10031B)", 
                       variable=pattern_var, value="numbers_only").pack(pady=2, anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Clean whitespace (trim + remove double spaces: ' SH  10031 ' → 'SH 10031')", 
                       variable=pattern_var, value="whitespace").pack(pady=2, anchor='w', padx=50)
        ttk.Radiobutton(dialog, text="Custom pattern (specify what to remove)", 
                       variable=pattern_var, value="custom").pack(pady=2, anchor='w', padx=50)
        
        # Position selector
        ttk.Label(dialog, text="Remove from:", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        position_var = tk.StringVar(value="end")
        position_frame = ttk.Frame(dialog)
        position_frame.pack(pady=5, padx=50)
        ttk.Radiobutton(position_frame, text="End (e.g., SH10031B1 → SH10031B)", 
                       variable=position_var, value="end").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(position_frame, text="Start (e.g., 1SH10031B → SH10031B)", 
                       variable=position_var, value="start").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(position_frame, text="Both sides", 
                       variable=position_var, value="both").pack(side=tk.LEFT, padx=10)
        
        # Custom pattern input
        custom_frame = ttk.Frame(dialog)
        custom_frame.pack(pady=5, padx=50, fill=tk.X)
        ttk.Label(custom_frame, text="Custom pattern:").pack(side=tk.LEFT, padx=5)
        custom_pattern_var = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=custom_pattern_var, width=20)
        custom_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(custom_frame, text="(e.g., '1' or '[0-9]+' for numbers)", 
                 font=('Arial', 8), foreground='gray').pack(side=tk.LEFT)
        
        # Preview area
        preview_frame = ttk.LabelFrame(dialog, text="Preview Changes", padding=10)
        preview_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)
        
        preview_text = tk.Text(preview_frame, height=10, width=60, wrap=tk.NONE)
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
        preview_text.config(yscrollcommand=preview_scroll.set)
        preview_text.grid(row=0, column=0, sticky='nsew')
        preview_scroll.grid(row=0, column=1, sticky='ns')
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_text.config(state=tk.DISABLED)
        
        def show_preview():
            """Show preview of changes"""
            col = col_var.get()
            if not col:
                messagebox.showwarning("Warning", "Please select a column!")
                return
            
            pattern = pattern_var.get()
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                position = position_var.get()
                
                # Special handling for whitespace cleaning
                if pattern == "whitespace":
                    whitespace_issues = df[col].astype(str)
                    needs_cleaning = (whitespace_issues != whitespace_issues.str.strip()) | \
                                   (whitespace_issues.str.contains(r'\s{2,}', regex=True, na=False))
                    affected = df[needs_cleaning]
                    
                    if len(affected) == 0:
                        preview_text.insert(tk.END, "✓ No whitespace issues found\n")
                        preview_text.insert(tk.END, "All Order IDs are already clean!\n")
                    else:
                        preview_text.insert(tk.END, f"📋 Found {len(affected)} ID(s) with whitespace issues:\n\n")
                        preview_text.insert(tk.END, f"{'Original ID':<25} → {'Cleaned ID':<25}\n")
                        preview_text.insert(tk.END, "=" * 55 + "\n")
                        
                        for idx in affected.index[:20]:
                            original_id = str(df.loc[idx, col])
                            cleaned_id = re.sub(r'\s+', ' ', original_id).strip()
                            preview_text.insert(tk.END, f"'{original_id}'<{len(original_id):<3} → '{cleaned_id}'<{len(cleaned_id):<3}\n")
                        
                        if len(affected) > 20:
                            preview_text.insert(tk.END, f"\n... and {len(affected) - 20} more\n")
                else:
                    # Determine base pattern for letter/number removal
                    if pattern == "all_letters":
                        base_pattern = r'[A-Z]+'
                        pattern_desc = "letters"
                    elif pattern == "single_letter":
                        base_pattern = r'[A-Z]'
                        pattern_desc = "single letter"
                    elif pattern == "numbers_only":
                        base_pattern = r'[0-9]+'
                        pattern_desc = "numbers"
                    elif pattern == "custom":
                        custom_pat = custom_pattern_var.get()
                        if not custom_pat:
                            preview_text.insert(tk.END, "⚠️ Please enter a custom pattern to remove\n")
                            preview_text.config(state=tk.DISABLED)
                            return
                        base_pattern = custom_pat
                        pattern_desc = f"custom pattern '{custom_pat}'"
                    
                    # Apply position anchors
                    if position == "end":
                        regex_pattern = base_pattern + '$'
                        position_desc = "at end"
                    elif position == "start":
                        regex_pattern = '^' + base_pattern
                        position_desc = "at start"
                    else:  # both
                        regex_pattern = f'^{base_pattern}|{base_pattern}$'
                        position_desc = "at start or end"
                    
                    affected = df[df[col].astype(str).str.contains(regex_pattern, regex=True, na=False)]
                    
                    if len(affected) == 0:
                        preview_text.insert(tk.END, f"✓ No IDs found with {pattern_desc} {position_desc}\n")
                        preview_text.insert(tk.END, "All Order IDs are already clean!\n")
                    else:
                        preview_text.insert(tk.END, f"📋 Found {len(affected)} ID(s) with {pattern_desc} {position_desc}:\n\n")
                        preview_text.insert(tk.END, f"{'Original ID':<20} → {'Cleaned ID':<20}\n")
                        preview_text.insert(tk.END, "=" * 45 + "\n")
                        
                        for original_id in affected[col].head(20):
                            cleaned_id = str(original_id).strip()
                            cleaned_id = re.sub(regex_pattern, '', cleaned_id)
                            preview_text.insert(tk.END, f"{str(original_id):<20} → {cleaned_id:<20}\n")
                    
                    if len(affected) > 20:
                        preview_text.insert(tk.END, f"\n... and {len(affected) - 20} more\n")
                
            except Exception as e:
                preview_text.insert(tk.END, f"❌ Error: {str(e)}")
            
            preview_text.config(state=tk.DISABLED)
        
        def apply_cleaning():
            """Apply the cleaning"""
            col = col_var.get()
            if not col:
                messagebox.showwarning("Warning", "Please select a column!")
                return
            
            pattern = pattern_var.get()
            before_count = len(df)
            result_df = df.copy()
            
            try:
                position = position_var.get()
                
                # Special handling for whitespace cleaning
                if pattern == "whitespace":
                    whitespace_issues = result_df[col].astype(str)
                    needs_cleaning = (whitespace_issues != whitespace_issues.str.strip()) | \
                                   (whitespace_issues.str.contains(r'\s{2,}', regex=True, na=False))
                    affected_count = needs_cleaning.sum()
                    
                    result_df[col] = result_df[col].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
                    
                    pattern_desc = "whitespace (trim + collapse multiple spaces)"
                    position_desc = ""
                else:
                    # Determine base pattern for letter/number removal
                    if pattern == "all_letters":
                        base_pattern = r'[A-Z]+'
                        pattern_desc = "letters"
                    elif pattern == "single_letter":
                        base_pattern = r'[A-Z]'
                        pattern_desc = "single letter"
                    elif pattern == "numbers_only":
                        base_pattern = r'[0-9]+'
                        pattern_desc = "numbers"
                    elif pattern == "custom":
                        custom_pat = custom_pattern_var.get()
                        if not custom_pat:
                            messagebox.showwarning("Warning", "Please enter a custom pattern!")
                            return
                        base_pattern = custom_pat
                        pattern_desc = f"custom pattern '{custom_pat}'"
                    
                    # Apply position anchors
                    if position == "end":
                        regex_pattern = base_pattern + '$'
                        position_desc = "at end"
                    elif position == "start":
                        regex_pattern = '^' + base_pattern
                        position_desc = "at start"
                    else:  # both
                        regex_pattern = f'^{base_pattern}|{base_pattern}$'
                        position_desc = "at start or end"
                    
                    # Count affected rows before cleaning
                    affected = result_df[result_df[col].astype(str).str.contains(regex_pattern, regex=True, na=False)]
                    affected_count = len(affected)
                    
                    # Safety check: Detect if any IDs would become empty
                    test_cleaned = affected[col].astype(str).str.replace(regex_pattern, '', regex=True)
                    empty_after_clean = test_cleaned[test_cleaned.str.strip() == '']
                    
                    if len(empty_after_clean) > 0:
                        warning_msg = f"⚠️ WARNING: This pattern would COMPLETELY REMOVE {len(empty_after_clean)} Order ID(s)!\n\n"
                        warning_msg += "These IDs would become empty:\n"
                        empty_indices = empty_after_clean.index.tolist()[:10]
                        for idx in empty_indices:
                            original_value = result_df.loc[idx, col]
                            warning_msg += f"  • {original_value}\n"
                        if len(empty_after_clean) > 10:
                            warning_msg += f"  ... and {len(empty_after_clean) - 10} more\n"
                        warning_msg += f"\nThis might DELETE your entire Order ID column!\n\n"
                        warning_msg += "Are you SURE you want to proceed?\n"
                        warning_msg += "(Hint: Try a different pattern or position)"
                        
                        confirm = messagebox.askyesno("⚠️ Destructive Operation Warning", 
                                                     warning_msg, 
                                                     icon='warning',
                                                     default='no')
                        if not confirm:
                            return
                    
                    # Apply cleaning
                    result_df[col] = result_df[col].astype(str).str.replace(regex_pattern, '', regex=True)
                
                # Build output message
                output_msg = "=" * 80 + "\n"
                output_msg += "CLEAN ORDER IDs - OPERATION COMPLETE\n"
                output_msg += "=" * 80 + "\n\n"
                output_msg += f"Column cleaned: {col}\n"
                output_msg += f"Removed: {pattern_desc} {position_desc}\n\n"
                output_msg += f"✓ Total rows: {before_count}\n"
                output_msg += f"✓ IDs cleaned: {affected_count}\n\n"
                output_msg += "=" * 80 + "\n"
                
                if affected_count > 0:
                    output_msg += f"SUCCESS: Cleaned {affected_count} Order ID(s)\n"
                    output_msg += "Examples: SH10031B → SH10031, SH10005A → SH10005\n"
                else:
                    output_msg += "INFO: No Order IDs needed cleaning\n"
                
                # Build status message
                status_msg = f"Cleaned {affected_count} Order IDs"
                
                # Call callback
                on_complete_callback(result_df, col, affected_count, status_msg, output_msg)
                
                messagebox.showinfo("Success", 
                                  f"Order IDs cleaned successfully!\n\n"
                                  f"Column: {col}\n"
                                  f"IDs cleaned: {affected_count}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clean Order IDs:\n{str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Preview Changes", 
                  command=show_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Apply Cleaning", command=apply_cleaning, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def confirm_trim_all_columns(parent, df, cleaning_service, on_complete_callback):
        """
        Confirm and trim all text columns
        
        Args:
            parent: Parent window
            df: DataFrame to process
            cleaning_service: CleaningService instance
            on_complete_callback: Callback function(cleaned_df, count, status_msg)
        """
        text_cols = df.select_dtypes(include=['object']).columns
        
        if messagebox.askyesno("Confirm", 
                              f"Trim whitespace from all {len(text_cols)} text columns?\n\n"
                              f"This will remove leading and trailing spaces.",
                              parent=parent):
            try:
                cleaned_df = cleaning_service.trim_all_columns(df)
                status_msg = f"Trimmed {len(text_cols)} columns"
                on_complete_callback(cleaned_df, len(text_cols), status_msg)
                messagebox.showinfo("Success", f"Trimmed {len(text_cols)} columns!", parent=parent)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to trim columns: {str(e)}", parent=parent)
    
    @staticmethod
    def show_convert_dtypes_dialog(parent, df, output_callback, notebook_callback, info_panel_callback, status_callback):
        """
        Show convert data types dialog
        
        Args:
            parent: Parent window
            df: DataFrame to modify
            output_callback: Callback function(text) to display output
            notebook_callback: Callback to switch to output tab
            info_panel_callback: Callback to update info panel
            status_callback: Callback to update status
        Returns:
            modified DataFrame or None
        """
        dialog = tk.Toplevel(parent)
        dialog.title("Convert Data Types")
        dialog.geometry("550x550")
        
        ttk.Label(dialog, text="Convert Column Data Type - Advanced", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Column selection with current type display
        col_frame = ttk.Frame(dialog)
        col_frame.pack(pady=10, fill=tk.X, padx=20)
        
        ttk.Label(col_frame, text="Select column:", font=('Arial', 10, 'bold')).pack(anchor='w')
        col_var = tk.StringVar(value=df.columns[0])
        col_dropdown = ttk.Combobox(col_frame, textvariable=col_var, 
                                    values=list(df.columns), state='readonly', width=35)
        col_dropdown.pack(pady=5)
        
        current_type_label = ttk.Label(col_frame, text="", font=('Arial', 9), foreground='gray')
        current_type_label.pack(anchor='w')
        
        def update_current_type(*args):
            col = col_var.get()
            current_type = str(df[col].dtype)
            current_type_label.config(text=f"Current type: {current_type}")
        
        col_var.trace('w', update_current_type)
        update_current_type()
        
        # Target type selection
        ttk.Label(dialog, text="Convert to:", font=('Arial', 10, 'bold')).pack(pady=(10,5))
        
        type_var = tk.StringVar(value="numeric")
        type_frame = ttk.Frame(dialog)
        type_frame.pack(pady=5)
        
        ttk.Radiobutton(type_frame, text="Numeric (float)", 
                       variable=type_var, value="numeric").grid(row=0, column=0, sticky='w', padx=10)
        ttk.Radiobutton(type_frame, text="Integer", 
                       variable=type_var, value="integer").grid(row=1, column=0, sticky='w', padx=10)
        ttk.Radiobutton(type_frame, text="String/Text", 
                       variable=type_var, value="string").grid(row=2, column=0, sticky='w', padx=10)
        ttk.Radiobutton(type_frame, text="DateTime", 
                       variable=type_var, value="datetime").grid(row=0, column=1, sticky='w', padx=10)
        ttk.Radiobutton(type_frame, text="Boolean (True/False)", 
                       variable=type_var, value="boolean").grid(row=1, column=1, sticky='w', padx=10)
        ttk.Radiobutton(type_frame, text="Category", 
                       variable=type_var, value="category").grid(row=2, column=1, sticky='w', padx=10)
        
        # Error handling
        ttk.Label(dialog, text="Error handling:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        error_var = tk.StringVar(value="coerce")
        error_frame = ttk.Frame(dialog)
        error_frame.pack(pady=5)
        
        ttk.Radiobutton(error_frame, text="Coerce (set invalid to NaN)", 
                       variable=error_var, value="coerce").pack(anchor='w', padx=50)
        ttk.Radiobutton(error_frame, text="Raise error if any invalid", 
                       variable=error_var, value="raise").pack(anchor='w', padx=50)
        ttk.Radiobutton(error_frame, text="Ignore (keep original)", 
                       variable=error_var, value="ignore").pack(anchor='w', padx=50)
        
        # DateTime format (conditional)
        datetime_frame = ttk.LabelFrame(dialog, text="DateTime Format (optional)", padding=10)
        datetime_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Label(datetime_frame, text="Format string (e.g., '%Y-%m-%d', '%m/%d/%Y'):").pack(anchor='w')
        format_var = tk.StringVar(value="")
        ttk.Entry(datetime_frame, textvariable=format_var, width=40).pack(pady=5)
        ttk.Label(datetime_frame, text="Leave blank for automatic detection", 
                 font=('Arial', 8), foreground='gray').pack(anchor='w')
        
        # Preview area
        preview_frame = ttk.LabelFrame(dialog, text="Preview", padding=10)
        preview_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        preview_text = tk.Text(preview_frame, height=6, width=60, wrap=tk.WORD)
        preview_text.pack(fill=tk.BOTH, expand=True)
        preview_text.config(state=tk.DISABLED)
        
        result = [None]  # Use list to store result
        
        def preview_conversion():
            """Show preview of conversion"""
            col = col_var.get()
            dtype = type_var.get()
            error_handling = error_var.get()
            
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                # Test conversion on sample
                sample = df[col].head(10).copy()
                
                if dtype == "numeric":
                    converted = pd.to_numeric(sample, errors=error_handling)
                elif dtype == "integer":
                    converted = pd.to_numeric(sample, errors=error_handling)
                    if error_handling != "ignore":
                        converted = converted.astype('Int64')
                elif dtype == "string":
                    converted = sample.astype(str)
                elif dtype == "datetime":
                    fmt = format_var.get() if format_var.get() else None
                    converted = pd.to_datetime(sample, format=fmt, errors=error_handling)
                elif dtype == "boolean":
                    converted = sample.astype(bool)
                elif dtype == "category":
                    converted = sample.astype('category')
                
                preview_text.insert(tk.END, "✅ Conversion Preview (first 10 rows):\n\n")
                preview_text.insert(tk.END, f"Original → Converted\n")
                preview_text.insert(tk.END, "-" * 50 + "\n")
                
                for orig, conv in zip(sample, converted):
                    preview_text.insert(tk.END, f"{orig} → {conv}\n")
                
                preview_text.insert(tk.END, f"\n✓ Target type: {dtype}")
                
            except Exception as e:
                preview_text.insert(tk.END, f"❌ Preview failed:\n{str(e)}\n\n")
                preview_text.insert(tk.END, "Tip: Try changing error handling to 'coerce'")
            
            preview_text.config(state=tk.DISABLED)
        
        def convert():
            """Perform actual conversion"""
            col = col_var.get()
            dtype = type_var.get()
            error_handling = error_var.get()
            
            try:
                old_dtype = str(df[col].dtype)
                df_copy = df.copy()
                
                if dtype == "numeric":
                    df_copy[col] = pd.to_numeric(df_copy[col], errors=error_handling)
                elif dtype == "integer":
                    df_copy[col] = pd.to_numeric(df_copy[col], errors=error_handling)
                    if error_handling != "ignore":
                        df_copy[col] = df_copy[col].astype('Int64')
                elif dtype == "string":
                    df_copy[col] = df_copy[col].astype(str)
                elif dtype == "datetime":
                    fmt = format_var.get() if format_var.get() else None
                    df_copy[col] = pd.to_datetime(df_copy[col], format=fmt, errors=error_handling)
                elif dtype == "boolean":
                    df_copy[col] = df_copy[col].astype(bool)
                elif dtype == "category":
                    df_copy[col] = df_copy[col].astype('category')
                
                new_dtype = str(df_copy[col].dtype)
                result[0] = df_copy
                
                # Output to text area
                output = []
                output.append("=" * 80)
                output.append("CONVERT DATA TYPES - OPERATION COMPLETE")
                output.append("=" * 80)
                output.append("")
                output.append(f"Column: {col}")
                output.append(f"Old type: {old_dtype}")
                output.append(f"New type: {new_dtype}")
                output.append(f"Error handling: {error_handling}")
                
                if dtype == "datetime" and format_var.get():
                    output.append(f"Date format used: {format_var.get()}")
                
                output.append("")
                output.append("=" * 80)
                output.append(f"SUCCESS: Column type converted successfully")
                output.append(f"Total rows: {len(df_copy)}")
                
                output_callback("\n".join(output))
                notebook_callback()
                info_panel_callback()
                status_callback(f"Converted {col} to {dtype}")
                
                messagebox.showinfo("Success", 
                                  f"Column '{col}' converted successfully!\n\n"
                                  f"Old type: {old_dtype}\n"
                                  f"New type: {new_dtype}\n"
                                  f"Error handling: {error_handling}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Preview", command=preview_conversion).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Convert", command=convert, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to close
        parent.wait_window(dialog)
        return result[0]
