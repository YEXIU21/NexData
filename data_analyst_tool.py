"""
Professional Data Analysis Tool
A comprehensive tool for data analysts with data import, cleaning, analysis, and visualization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import os
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')
sns.set_style('whitegrid')


class DataAnalystTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Data Analysis Tool")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        self.df = None
        self.original_df = None
        self.file_path = None
        
        self.setup_styles()
        self.create_menu()
        self.create_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Action.TButton', font=('Arial', 10, 'bold'), padding=5)
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Import Excel", command=self.import_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_command(label="Export Excel", command=self.export_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Data", menu=data_menu)
        data_menu.add_command(label="View Data", command=self.view_data)
        data_menu.add_command(label="Data Info", command=self.show_data_info)
        data_menu.add_command(label="Statistics", command=self.show_statistics)
        data_menu.add_command(label="Reset Data", command=self.reset_data)
        
        clean_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Clean", menu=clean_menu)
        clean_menu.add_command(label="Remove Duplicates", command=self.remove_duplicates)
        clean_menu.add_command(label="Handle Missing Values", command=self.handle_missing_values)
        clean_menu.add_command(label="Remove Outliers", command=self.remove_outliers)
        
        viz_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualize", menu=viz_menu)
        viz_menu.add_command(label="Histogram", command=self.plot_histogram)
        viz_menu.add_command(label="Box Plot", command=self.plot_boxplot)
        viz_menu.add_command(label="Scatter Plot", command=self.plot_scatter)
        viz_menu.add_command(label="Correlation Heatmap", command=self.plot_heatmap)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_ui(self):
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(title_frame, text="Professional Data Analysis Tool", style='Title.TLabel').pack()
        
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel
        left_panel = ttk.Frame(self.main_paned, relief=tk.RIDGE, borderwidth=2)
        self.main_paned.add(left_panel, weight=1)
        
        ttk.Label(left_panel, text="Quick Actions", style='Header.TLabel').pack(pady=10)
        
        actions_frame = ttk.Frame(left_panel)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Import CSV", command=self.import_csv, style='Action.TButton').pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Import Excel", command=self.import_excel, style='Action.TButton').pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="View Data", command=self.view_data, style='Action.TButton').pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Statistics", command=self.show_statistics, style='Action.TButton').pack(fill=tk.X, pady=2)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(left_panel, text="Dataset Info", style='Header.TLabel').pack(pady=10)
        
        self.info_text = scrolledtext.ScrolledText(left_panel, height=15, width=40, font=('Courier', 9), wrap=tk.WORD)
        self.info_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Right panel
        right_panel = ttk.Frame(self.main_paned, relief=tk.RIDGE, borderwidth=2)
        self.main_paned.add(right_panel, weight=3)
        
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        output_frame = ttk.Frame(self.notebook)
        self.notebook.add(output_frame, text="Output")
        self.output_text = scrolledtext.ScrolledText(output_frame, height=30, font=('Courier', 10), wrap=tk.NONE)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualization")
        self.viz_canvas_frame = ttk.Frame(viz_frame)
        self.viz_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_bar = ttk.Label(self.root, text="Ready | No data loaded", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.update_info_panel()
        
    def update_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"{timestamp} | {message}")
        
    def update_info_panel(self):
        self.info_text.delete(1.0, tk.END)
        
        if self.df is None:
            self.info_text.insert(tk.END, "No data loaded.\n\nUse File menu to import:\n- CSV files\n- Excel files")
        else:
            info = f"File: {os.path.basename(self.file_path) if self.file_path else 'N/A'}\n\n"
            info += f"Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns\n\nColumns:\n"
            for col in self.df.columns[:15]:
                info += f"  • {col} ({self.df[col].dtype})\n"
            if len(self.df.columns) > 15:
                info += f"  ... and {len(self.df.columns) - 15} more\n"
            
            missing = self.df.isnull().sum().sum()
            if missing > 0:
                info += f"\nMissing Values: {missing}\n"
            
            self.info_text.insert(tk.END, info)
    
    def import_csv(self):
        file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.original_df = self.df.copy()
                self.file_path = file_path
                self.update_status(f"Loaded: {os.path.basename(file_path)}")
                self.update_info_panel()
                self.view_data()
                messagebox.showinfo("Success", f"CSV loaded!\n{self.df.shape[0]} rows, {self.df.shape[1]} cols")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")
    
    def import_excel(self):
        file_path = filedialog.askopenfilename(title="Select Excel file", filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")])
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.original_df = self.df.copy()
                self.file_path = file_path
                self.update_status(f"Loaded: {os.path.basename(file_path)}")
                self.update_info_panel()
                self.view_data()
                messagebox.showinfo("Success", f"Excel loaded!\n{self.df.shape[0]} rows, {self.df.shape[1]} cols")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Excel:\n{str(e)}")
    
    def export_csv(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
                self.update_status(f"Exported to CSV")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_excel(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                self.df.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
                self.update_status(f"Exported to Excel")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def view_data(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"=== DATA VIEW (First 100 rows) ===\n\n{self.df.head(100).to_string()}")
        self.notebook.select(0)
        self.update_status("Displaying data")
    
    def show_data_info(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=== DATA INFORMATION ===\n\n")
        
        info_str = f"Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns\n\n"
        for col in self.df.columns:
            non_null = self.df[col].notna().sum()
            null_count = self.df[col].isna().sum()
            info_str += f"{col}: {self.df[col].dtype} | Non-Null: {non_null} | Null: {null_count} | Unique: {self.df[col].nunique()}\n"
        
        self.output_text.insert(tk.END, info_str)
        self.notebook.select(0)
        self.update_status("Data information displayed")
    
    def show_statistics(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=== STATISTICAL SUMMARY ===\n\n")
        self.output_text.insert(tk.END, self.df.describe().to_string())
        self.notebook.select(0)
        self.update_status("Statistics displayed")
    
    def reset_data(self):
        if self.original_df is None:
            messagebox.showwarning("Warning", "No original data!")
            return
        if messagebox.askyesno("Confirm", "Reset to original data?"):
            self.df = self.original_df.copy()
            self.update_info_panel()
            self.view_data()
            self.update_status("Data reset")
    
    def remove_duplicates(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = before - len(self.df)
        self.update_info_panel()
        self.update_status(f"Removed {removed} duplicates")
        messagebox.showinfo("Success", f"Removed {removed} duplicate rows")
    
    def handle_missing_values(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Handle Missing Values")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text=f"Missing: {self.df.isnull().sum().sum()}", font=('Arial', 12, 'bold')).pack(pady=10)
        
        method_var = tk.StringVar(value="drop")
        ttk.Radiobutton(dialog, text="Drop rows", variable=method_var, value="drop").pack(pady=5)
        ttk.Radiobutton(dialog, text="Fill with mean", variable=method_var, value="mean").pack(pady=5)
        ttk.Radiobutton(dialog, text="Fill with median", variable=method_var, value="median").pack(pady=5)
        ttk.Radiobutton(dialog, text="Forward fill", variable=method_var, value="ffill").pack(pady=5)
        
        def apply():
            method = method_var.get()
            if method == "drop":
                self.df = self.df.dropna()
            elif method == "mean":
                self.df.fillna(self.df.mean(numeric_only=True), inplace=True)
            elif method == "median":
                self.df.fillna(self.df.median(numeric_only=True), inplace=True)
            elif method == "ffill":
                self.df.fillna(method='ffill', inplace=True)
            
            self.update_info_panel()
            self.update_status(f"Handled missing values: {method}")
            messagebox.showinfo("Success", f"Applied {method} method")
            dialog.destroy()
        
        ttk.Button(dialog, text="Apply", command=apply).pack(pady=20)
    
    def remove_outliers(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        before = len(self.df)
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            self.df = self.df[(self.df[col] >= Q1 - 1.5*IQR) & (self.df[col] <= Q3 + 1.5*IQR)]
        
        removed = before - len(self.df)
        self.update_info_panel()
        self.update_status(f"Removed {removed} outliers")
        messagebox.showinfo("Success", f"Removed {removed} outlier rows")
    
    def plot_histogram(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Column for Histogram")
        ttk.Label(dialog, text="Select column:").pack(pady=10)
        
        col_var = tk.StringVar(value=numeric_cols[0])
        combo = ttk.Combobox(dialog, textvariable=col_var, values=numeric_cols, state='readonly')
        combo.pack(pady=5)
        
        def plot():
            self.create_plot(lambda fig: self.df[col_var.get()].hist(ax=fig.gca(), bins=30, edgecolor='black'))
            dialog.destroy()
        
        ttk.Button(dialog, text="Plot", command=plot).pack(pady=10)
    
    def plot_boxplot(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns!")
            return
        
        self.create_plot(lambda fig: self.df[numeric_cols].boxplot(ax=fig.gca()))
    
    def plot_scatter(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            messagebox.showwarning("Warning", "Need at least 2 numeric columns!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Columns for Scatter Plot")
        ttk.Label(dialog, text="X axis:").pack(pady=5)
        x_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(dialog, textvariable=x_var, values=numeric_cols, state='readonly').pack()
        
        ttk.Label(dialog, text="Y axis:").pack(pady=5)
        y_var = tk.StringVar(value=numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])
        ttk.Combobox(dialog, textvariable=y_var, values=numeric_cols, state='readonly').pack()
        
        def plot():
            self.create_plot(lambda fig: self.df.plot.scatter(x=x_var.get(), y=y_var.get(), ax=fig.gca(), alpha=0.6))
            dialog.destroy()
        
        ttk.Button(dialog, text="Plot", command=plot).pack(pady=10)
    
    def plot_heatmap(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            messagebox.showwarning("Warning", "Need at least 2 numeric columns!")
            return
        
        corr = self.df[numeric_cols].corr()
        self.create_plot(lambda fig: sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', ax=fig.gca(), square=True))
    
    def create_plot(self, plot_func):
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
        
        fig = plt.Figure(figsize=(10, 7), dpi=100)
        plot_func(fig)
        
        canvas = FigureCanvasTkAgg(fig, self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.notebook.select(1)
        self.update_status("Plot created")
    
    def show_about(self):
        messagebox.showinfo("About", "Professional Data Analysis Tool v1.0\n\nCreated for data analyst professionals\n\nFeatures:\n- Import/Export data\n- Data cleaning\n- Statistical analysis\n- Data visualization")


def main():
    root = tk.Tk()
    app = DataAnalystTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
