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
