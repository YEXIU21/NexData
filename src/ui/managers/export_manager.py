"""
Export Manager
Handles data export operations
Extracted from main_window.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.utils.excel_pivot_exporter import ExcelPivotExporter


class ExportManager:
    """Manages data export operations"""
    
    def __init__(self, app):
        """
        Initialize Export Manager
        
        Args:
            app: Reference to main application
        """
        self.app = app
    
    def export_csv(self):
        """Export data to CSV"""
        if self.app.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.app.data_service.export_csv(self.app.df, file_path)
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
                self.app.update_status(f"Exported to CSV")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_excel(self):
        """Export data to Excel"""
        if self.app.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                self.app.data_service.export_excel(self.app.df, file_path)
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
                self.app.update_status(f"Exported to Excel")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_json(self):
        """Export data to JSON"""
        if self.app.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                self.app.data_service.export_json(self.app.df, file_path)
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
                self.app.update_status(f"Exported to JSON")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_excel_with_pivot(self):
        """Export Excel with pivot table configuration dialog"""
        if self.app.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        # Create configuration dialog
        pivot_window = tk.Toplevel(self.app.root)
        pivot_window.title("Export Excel with Pivot Table")
        pivot_window.geometry("500x450")
        pivot_window.transient(self.app.root)
        pivot_window.grab_set()
        
        # Title
        ttk.Label(pivot_window, text="Configure Pivot Table Export", style='Header.TLabel').pack(pady=10)
        
        # Frame for configuration
        config_frame = ttk.Frame(pivot_window, padding=20)
        config_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get column names
        columns = list(self.app.df.columns)
        
        # Index (Rows) selection
        ttk.Label(config_frame, text="Row Field (Index):").grid(row=0, column=0, sticky='w', pady=5)
        index_var = tk.StringVar()
        index_combo = ttk.Combobox(config_frame, textvariable=index_var, values=columns, width=30)
        index_combo.grid(row=0, column=1, pady=5, padx=5)
        if columns:
            index_combo.current(0)
        
        # Columns selection
        ttk.Label(config_frame, text="Column Field (optional):").grid(row=1, column=0, sticky='w', pady=5)
        column_var = tk.StringVar()
        column_combo = ttk.Combobox(config_frame, textvariable=column_var, values=['None'] + columns, width=30)
        column_combo.grid(row=1, column=1, pady=5, padx=5)
        column_combo.current(0)
        
        # Values selection
        ttk.Label(config_frame, text="Value Field:").grid(row=2, column=0, sticky='w', pady=5)
        value_var = tk.StringVar()
        
        # Filter numeric columns for values
        numeric_columns = list(self.app.df.select_dtypes(include=['number']).columns)
        if not numeric_columns:
            numeric_columns = columns
        
        value_combo = ttk.Combobox(config_frame, textvariable=value_var, values=numeric_columns, width=30)
        value_combo.grid(row=2, column=1, pady=5, padx=5)
        if numeric_columns:
            value_combo.current(0)
        
        # Aggregation function
        ttk.Label(config_frame, text="Aggregation Function:").grid(row=3, column=0, sticky='w', pady=5)
        aggfunc_var = tk.StringVar(value='sum')
        aggfunc_combo = ttk.Combobox(config_frame, textvariable=aggfunc_var, 
                                     values=['sum', 'mean', 'count', 'min', 'max', 'median'], 
                                     width=30)
        aggfunc_combo.grid(row=3, column=1, pady=5, padx=5)
        
        # Add chart checkbox
        add_chart_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Include Bar Chart", variable=add_chart_var).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Result label
        result_label = ttk.Label(config_frame, text="", foreground="blue")
        result_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        def perform_export():
            """Perform the export with pivot"""
            try:
                # Get file path
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx", 
                    filetypes=[("Excel files", "*.xlsx")],
                    parent=pivot_window
                )
                
                if not file_path:
                    return
                
                # Build pivot configuration
                pivot_config = {
                    'index': index_var.get(),
                    'columns': None if column_var.get() == 'None' else column_var.get(),
                    'values': value_var.get(),
                    'aggfunc': aggfunc_var.get()
                }
                
                # Perform export
                result_label.config(text="Exporting...", foreground="blue")
                pivot_window.update()
                
                if add_chart_var.get():
                    success, message = ExcelPivotExporter.export_with_charts(
                        self.app.df, file_path, pivot_config, chart_type='bar'
                    )
                else:
                    success, message = ExcelPivotExporter.export_with_pivot(
                        self.app.df, file_path, pivot_config
                    )
                
                if success:
                    messagebox.showinfo("Success", message, parent=pivot_window)
                    self.app.update_status("Exported Excel with pivot table")
                    pivot_window.destroy()
                else:
                    result_label.config(text=f"Error: {message}", foreground="red")
            
            except Exception as e:
                result_label.config(text=f"Error: {str(e)}", foreground="red")
                messagebox.showerror("Error", f"Export failed:\n{str(e)}", parent=pivot_window)
        
        # Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Export", command=perform_export, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=pivot_window.destroy).pack(side=tk.LEFT, padx=5)
