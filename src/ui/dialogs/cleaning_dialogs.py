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
