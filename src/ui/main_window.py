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


class DataAnalystApp:
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
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Generate Executive Report (HTML)", command=self.generate_executive_report)
        file_menu.add_command(label="Generate Quick Summary", command=self.generate_quick_summary)
        file_menu.add_command(label="Format for Email", command=self.format_for_email)
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
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="SQL Query", command=self.sql_query)
        analysis_menu.add_command(label="Data Profiling Report", command=self.data_profiling_report)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Column Analysis", command=self.column_analysis)
        analysis_menu.add_command(label="Correlation Analysis", command=self.correlation_analysis)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Statistical Tests", command=self.statistical_tests)
        analysis_menu.add_command(label="A/B Testing", command=self.ab_testing)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Time Series Analysis", command=self.time_series_analysis)
        analysis_menu.add_command(label="E-commerce Dashboard", command=self.ecommerce_dashboard)
        
        viz_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualize", menu=viz_menu)
        viz_menu.add_command(label="Histogram", command=self.plot_histogram)
        viz_menu.add_command(label="Box Plot", command=self.plot_boxplot)
        viz_menu.add_command(label="Scatter Plot", command=self.plot_scatter)
        viz_menu.add_command(label="Pie Chart", command=self.plot_pie)
        viz_menu.add_separator()
        viz_menu.add_command(label="Distribution Plot (KDE)", command=self.plot_distribution)
        viz_menu.add_command(label="Violin Plot", command=self.plot_violin)
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
            col = col_var.get()
            def plot_func(fig, ax):
                ax.hist(self.df[col].dropna(), bins=30, edgecolor='black', alpha=0.7)
                ax.set_title(f'Distribution of {col}', fontsize=14, fontweight='bold')
                ax.set_xlabel(col)
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
            self.create_plot(plot_func)
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
        
        def plot_func(fig, ax):
            data_to_plot = [self.df[col].dropna() for col in numeric_cols]
            ax.boxplot(data_to_plot, labels=numeric_cols)
            ax.set_title('Box Plot - Distribution Comparison', fontsize=14, fontweight='bold')
            ax.set_ylabel('Values')
            ax.grid(True, alpha=0.3, axis='y')
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self.create_plot(plot_func)
    
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
            x_col = x_var.get()
            y_col = y_var.get()
            def plot_func(fig, ax):
                ax.scatter(self.df[x_col], self.df[y_col], alpha=0.6, s=50)
                ax.set_title(f'{y_col} vs {x_col}', fontsize=14, fontweight='bold')
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.grid(True, alpha=0.3)
            self.create_plot(plot_func)
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
        self.create_plot(lambda fig, ax: sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', ax=ax, square=True))
    
    def create_plot(self, plot_func):
        # Clear previous plot
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
        
        # Create matplotlib figure - FIX: Use Figure from matplotlib.figure
        from matplotlib.figure import Figure
        fig = Figure(figsize=(12, 8), dpi=100)
        fig.patch.set_facecolor('white')
        
        # Create axis BEFORE passing to plot function
        ax = fig.add_subplot(111)
        
        # Execute plot function with figure AND axis
        try:
            plot_func(fig, ax)
        except Exception as e:
            messagebox.showerror("Plot Error", f"Failed to create plot:\n{str(e)}")
            return
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, self.viz_canvas_frame)
        toolbar.update()
        
        self.notebook.select(1)
        self.update_status("✓ Plot created successfully")
    
    def plot_pie(self):
        """Create pie chart"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Get categorical columns
        cat_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        if not cat_cols:
            messagebox.showwarning("Warning", "No categorical columns for pie chart!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Pie Chart")
        dialog.geometry("350x150")
        
        ttk.Label(dialog, text="Select column:", font=('Arial', 11)).pack(pady=10)
        col_var = tk.StringVar(value=cat_cols[0])
        ttk.Combobox(dialog, textvariable=col_var, values=cat_cols, state='readonly', width=30).pack(pady=5)
        
        def plot():
            col = col_var.get()
            value_counts = self.df[col].value_counts().head(10)
            
            def plot_func(fig, ax):
                ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
                ax.set_title(f'Distribution of {col}', fontsize=14, fontweight='bold')
            
            self.create_plot(plot_func)
            dialog.destroy()
        
        ttk.Button(dialog, text="Create Chart", command=plot).pack(pady=15)
    
    def plot_distribution(self):
        """Create distribution plot with KDE"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Distribution Plot")
        ttk.Label(dialog, text="Select column:").pack(pady=10)
        col_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(dialog, textvariable=col_var, values=numeric_cols, state='readonly').pack(pady=5)
        
        def plot():
            col = col_var.get()
            def plot_func(fig, ax):
                self.df[col].hist(ax=ax, bins=30, alpha=0.7, edgecolor='black', density=True, label='Histogram')
                self.df[col].plot(kind='kde', ax=ax, color='red', linewidth=2, label='KDE')
                ax.set_title(f'Distribution of {col}', fontsize=14, fontweight='bold')
                ax.set_xlabel(col)
                ax.set_ylabel('Density')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            self.create_plot(plot_func)
            dialog.destroy()
        
        ttk.Button(dialog, text="Plot", command=plot).pack(pady=10)
    
    def plot_violin(self):
        """Create violin plot"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns!")
            return
        
        def plot_func(fig, ax):
            data_to_plot = [self.df[col].dropna() for col in numeric_cols[:6]]
            ax.violinplot(data_to_plot, showmeans=True, showmedians=True)
            ax.set_xticks(range(1, len(numeric_cols[:6]) + 1))
            ax.set_xticklabels(numeric_cols[:6], rotation=45, ha='right')
            ax.set_title('Violin Plot - Distribution Comparison', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        self.create_plot(plot_func)
    
    def time_series_analysis(self):
        """Analyze time series data"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Find date columns
        date_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Also check object columns that might be dates
        for col in self.df.select_dtypes(include=['object']).columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(self.df[col].head())
                    date_cols.append(col)
                except:
                    pass
        
        if not date_cols:
            messagebox.showwarning("Warning", "No date columns found! Try converting a column to datetime first.")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns for analysis!")
            return
        
        dialog = tk.Toplevel(self.root)
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
            df_temp = self.df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col])
            df_temp = df_temp.sort_values(date_col)
            
            def plot_func(fig, ax):
                ax.plot(df_temp[date_col], df_temp[value_col], marker='o', linestyle='-', linewidth=2, markersize=4)
                ax.set_title(f'Time Series: {value_col} over Time', fontsize=14, fontweight='bold')
                ax.set_xlabel('Date')
                ax.set_ylabel(value_col)
                ax.grid(True, alpha=0.3)
                fig.autofmt_xdate()
            
            self.create_plot(plot_func)
            dialog.destroy()
        
        ttk.Button(dialog, text="Analyze", command=analyze).pack(pady=15)
    
    def ecommerce_dashboard(self):
        """Create e-commerce analytics dashboard"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "🛍️  E-COMMERCE ANALYTICS DASHBOARD\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        
        # Key metrics
        self.output_text.insert(tk.END, "📊 KEY METRICS:\n")
        self.output_text.insert(tk.END, "-" * 80 + "\n")
        self.output_text.insert(tk.END, f"Total Records: {len(self.df):,}\n")
        self.output_text.insert(tk.END, f"Date Range: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        # Find revenue-like columns
        revenue_cols = [col for col in self.df.columns if any(x in col.lower() for x in ['revenue', 'sales', 'price', 'amount', 'total'])]
        if revenue_cols:
            self.output_text.insert(tk.END, f"💰 REVENUE ANALYSIS:\n")
            for col in revenue_cols[:3]:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.output_text.insert(tk.END, f"  {col}:\n")
                    self.output_text.insert(tk.END, f"    Total: ${self.df[col].sum():,.2f}\n")
                    self.output_text.insert(tk.END, f"    Average: ${self.df[col].mean():,.2f}\n")
                    self.output_text.insert(tk.END, f"    Median: ${self.df[col].median():,.2f}\n\n")
        
        # Customer analysis
        customer_cols = [col for col in self.df.columns if 'customer' in col.lower() or 'user' in col.lower()]
        if customer_cols:
            self.output_text.insert(tk.END, f"👥 CUSTOMER INSIGHTS:\n")
            for col in customer_cols[:2]:
                unique_count = self.df[col].nunique()
                self.output_text.insert(tk.END, f"  Unique {col}: {unique_count:,}\n")
        
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n")
        self.output_text.insert(tk.END, "💡 Use Visualize menu for detailed charts\n")
        
        self.notebook.select(0)
        self.update_status("Dashboard generated")
    
    def column_analysis(self):
        """Detailed analysis of a specific column"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Column Analysis")
        dialog.geometry("350x150")
        
        ttk.Label(dialog, text="Select column to analyze:", font=('Arial', 11)).pack(pady=10)
        col_var = tk.StringVar(value=self.df.columns[0])
        ttk.Combobox(dialog, textvariable=col_var, values=list(self.df.columns), state='readonly', width=30).pack(pady=5)
        
        def analyze():
            col = col_var.get()
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"=" * 80 + "\n")
            self.output_text.insert(tk.END, f"COLUMN ANALYSIS: {col}\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n\n")
            
            self.output_text.insert(tk.END, f"Data Type: {self.df[col].dtype}\n")
            self.output_text.insert(tk.END, f"Non-Null Count: {self.df[col].notna().sum():,}\n")
            self.output_text.insert(tk.END, f"Null Count: {self.df[col].isna().sum():,}\n")
            self.output_text.insert(tk.END, f"Unique Values: {self.df[col].nunique():,}\n\n")
            
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.output_text.insert(tk.END, "STATISTICS:\n")
                self.output_text.insert(tk.END, f"  Mean: {self.df[col].mean():.2f}\n")
                self.output_text.insert(tk.END, f"  Median: {self.df[col].median():.2f}\n")
                self.output_text.insert(tk.END, f"  Std Dev: {self.df[col].std():.2f}\n")
                self.output_text.insert(tk.END, f"  Min: {self.df[col].min():.2f}\n")
                self.output_text.insert(tk.END, f"  Max: {self.df[col].max():.2f}\n\n")
            
            self.output_text.insert(tk.END, "TOP 10 VALUES:\n")
            value_counts = self.df[col].value_counts().head(10)
            self.output_text.insert(tk.END, value_counts.to_string())
            
            self.notebook.select(0)
            dialog.destroy()
        
        ttk.Button(dialog, text="Analyze", command=analyze).pack(pady=15)
    
    def filter_data(self):
        """Filter data interactively"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        messagebox.showinfo("Coming Soon", "Interactive filtering will be added in next version!")
    
    def sort_data(self):
        """Sort data by column"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Sort Data")
        dialog.geometry("350x180")
        
        ttk.Label(dialog, text="Sort by column:", font=('Arial', 11)).pack(pady=10)
        col_var = tk.StringVar(value=self.df.columns[0])
        ttk.Combobox(dialog, textvariable=col_var, values=list(self.df.columns), state='readonly', width=30).pack(pady=5)
        
        order_var = tk.StringVar(value="ascending")
        ttk.Radiobutton(dialog, text="Ascending", variable=order_var, value="ascending").pack(pady=3)
        ttk.Radiobutton(dialog, text="Descending", variable=order_var, value="descending").pack(pady=3)
        
        def sort():
            col = col_var.get()
            ascending = (order_var.get() == "ascending")
            self.df = self.df.sort_values(by=col, ascending=ascending)
            self.update_info_panel()
            self.view_data()
            self.update_status(f"Sorted by {col} ({order_var.get()})")
            messagebox.showinfo("Success", f"Data sorted by {col}")
            dialog.destroy()
        
        ttk.Button(dialog, text="Sort", command=sort).pack(pady=10)
    
    def convert_dtypes(self):
        """Convert column data types"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Convert Data Types")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="Select column:", font=('Arial', 11)).pack(pady=10)
        col_var = tk.StringVar(value=self.df.columns[0])
        ttk.Combobox(dialog, textvariable=col_var, values=list(self.df.columns), state='readonly', width=30).pack(pady=5)
        
        ttk.Label(dialog, text="Convert to:", font=('Arial', 11)).pack(pady=10)
        type_var = tk.StringVar(value="numeric")
        ttk.Radiobutton(dialog, text="Numeric (float)", variable=type_var, value="numeric").pack(pady=2)
        ttk.Radiobutton(dialog, text="Integer", variable=type_var, value="integer").pack(pady=2)
        ttk.Radiobutton(dialog, text="String", variable=type_var, value="string").pack(pady=2)
        ttk.Radiobutton(dialog, text="DateTime", variable=type_var, value="datetime").pack(pady=2)
        
        def convert():
            col = col_var.get()
            dtype = type_var.get()
            
            try:
                if dtype == "numeric":
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                elif dtype == "integer":
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce').astype('Int64')
                elif dtype == "string":
                    self.df[col] = self.df[col].astype(str)
                elif dtype == "datetime":
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                
                self.update_info_panel()
                self.update_status(f"Converted {col} to {dtype}")
                messagebox.showinfo("Success", f"Column {col} converted to {dtype}")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
        
        ttk.Button(dialog, text="Convert", command=convert).pack(pady=15)
    
    def groupby_analysis(self):
        """Group by analysis"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        messagebox.showinfo("Coming Soon", "Group by analysis will be added in next version!")
    
    def pivot_table_analysis(self):
        """Pivot table"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        messagebox.showinfo("Coming Soon", "Pivot table will be added in next version!")
    
    def correlation_analysis(self):
        """Correlation analysis"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            messagebox.showwarning("Warning", "Need at least 2 numeric columns!")
            return
        
        corr_matrix = self.df[numeric_cols].corr()
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "CORRELATION ANALYSIS\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        self.output_text.insert(tk.END, corr_matrix.to_string())
        self.output_text.insert(tk.END, "\n\n" + "=" * 80 + "\n")
        self.output_text.insert(tk.END, "💡 Use Visualize > Correlation Heatmap for visual representation\n")
        
        self.notebook.select(0)
        self.update_status("Correlation analysis completed")
    
    def copy_output(self):
        """Copy output to clipboard"""
        try:
            text = self.output_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.update_status("✓ Output copied to clipboard")
        except:
            messagebox.showerror("Error", "Failed to copy to clipboard")
    
    def save_output(self):
        """Save output to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Output",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.output_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Output saved to:\n{file_path}")
                self.update_status(f"✓ Output saved")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")
    
    def sql_query(self):
        """Execute SQL query on data"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        from data_ops.sql_interface import SQLInterface
        
        dialog = tk.Toplevel(self.root)
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
            result_df, error = SQLInterface.execute_query(self.df, query)
            
            if error:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"ERROR: {error}")
            else:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Rows returned: {len(result_df)}\n\n")
                result_text.insert(tk.END, result_df.to_string())
        
        ttk.Button(dialog, text="Execute Query", command=execute).pack(pady=10)
        self.update_status("SQL Query interface opened")
    
    def data_profiling_report(self):
        """Generate comprehensive data profiling report"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        from data_ops.sql_interface import DataProfiler
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "DATA PROFILING REPORT\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        
        profile = DataProfiler.generate_profile(self.df)
        
        # Overview
        self.output_text.insert(tk.END, "DATASET OVERVIEW:\n")
        self.output_text.insert(tk.END, "-" * 80 + "\n")
        for key, value in profile['overview'].items():
            self.output_text.insert(tk.END, f"  {key}: {value}\n")
        
        # Quality Score
        self.output_text.insert(tk.END, f"\n📊 DATA QUALITY SCORE: {profile['quality']['quality_score']}/100\n\n")
        
        # Issues
        if profile['quality']['total_issues'] > 0:
            self.output_text.insert(tk.END, f"⚠️ ISSUES FOUND ({profile['quality']['total_issues']}):\n")
            for issue in profile['quality']['issues'][:10]:
                self.output_text.insert(tk.END, f"  [{issue['severity']}] {issue['type']}: {issue['column']}\n")
        
        # Recommendations
        self.output_text.insert(tk.END, f"\n💡 RECOMMENDATIONS ({len(profile['recommendations'])}):\n")
        for rec in profile['recommendations']:
            self.output_text.insert(tk.END, f"  [{rec['priority']}] {rec['action']}: {rec['reason']}\n")
        
        # Strong correlations
        if profile['correlations'].get('strong_correlations'):
            self.output_text.insert(tk.END, f"\n🔗 STRONG CORRELATIONS:\n")
            for corr in profile['correlations']['strong_correlations'][:5]:
                self.output_text.insert(tk.END, f"  {corr['col1']} ↔ {corr['col2']}: {corr['correlation']:.3f} ({corr['strength']})\n")
        
        self.notebook.select(0)
        self.update_status("Data profiling report generated")
        messagebox.showinfo("Success", "Data profiling report generated!")
    
    def statistical_tests(self):
        """Perform statistical hypothesis tests"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        dialog = tk.Toplevel(self.root)
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
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
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
            
            if not col1 or col1 not in self.df.columns:
                messagebox.showerror("Error", "Please select valid Column 1")
                return
            
            try:
                result_text.delete(1.0, tk.END)
                
                if test_type == "t-test":
                    if not col2 or col2 not in self.df.columns:
                        messagebox.showerror("Error", "Please select valid Column 2")
                        return
                    result = HypothesisTesting.t_test_independent(self.df[col1], self.df[col2])
                    result_text.insert(tk.END, f"Independent T-Test: {col1} vs {col2}\n\n")
                
                elif test_type == "paired-t":
                    if not col2 or col2 not in self.df.columns:
                        messagebox.showerror("Error", "Please select valid Column 2")
                        return
                    result = HypothesisTesting.t_test_paired(self.df[col1], self.df[col2])
                    result_text.insert(tk.END, f"Paired T-Test: {col1} vs {col2}\n\n")
                
                elif test_type == "normality":
                    result = HypothesisTesting.normality_test(self.df[col1])
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
    
    def ab_testing(self):
        """A/B Testing analysis"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("A/B Testing")
        dialog.geometry("700x600")
        
        ttk.Label(dialog, text="A/B Test Analysis", font=('Arial', 14, 'bold')).pack(pady=10)
        
        test_type = tk.StringVar(value="conversion")
        ttk.Radiobutton(dialog, text="Conversion Rate Test", variable=test_type, value="conversion").pack(pady=5)
        ttk.Radiobutton(dialog, text="Continuous Metric Test (e.g., revenue, time)", variable=test_type, value="continuous").pack(pady=5)
        
        ttk.Label(dialog, text="\nFor Conversion Rate Test:", font=('Arial', 10, 'bold')).pack(pady=10)
        
        conv_frame = ttk.Frame(dialog)
        conv_frame.pack(pady=5)
        
        ttk.Label(conv_frame, text="Control Conversions:").grid(row=0, column=0, sticky='e', padx=5)
        control_conv_var = tk.StringVar(value="100")
        ttk.Entry(conv_frame, textvariable=control_conv_var, width=15).grid(row=0, column=1)
        
        ttk.Label(conv_frame, text="Control Total:").grid(row=1, column=0, sticky='e', padx=5)
        control_total_var = tk.StringVar(value="1000")
        ttk.Entry(conv_frame, textvariable=control_total_var, width=15).grid(row=1, column=1)
        
        ttk.Label(conv_frame, text="Treatment Conversions:").grid(row=0, column=2, sticky='e', padx=5)
        treatment_conv_var = tk.StringVar(value="120")
        ttk.Entry(conv_frame, textvariable=treatment_conv_var, width=15).grid(row=0, column=3)
        
        ttk.Label(conv_frame, text="Treatment Total:").grid(row=1, column=2, sticky='e', padx=5)
        treatment_total_var = tk.StringVar(value="1000")
        ttk.Entry(conv_frame, textvariable=treatment_total_var, width=15).grid(row=1, column=3)
        
        ttk.Label(dialog, text="\nFor Continuous Metric Test (select columns):", font=('Arial', 10, 'bold')).pack(pady=10)
        
        cont_frame = ttk.Frame(dialog)
        cont_frame.pack(pady=5)
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        ttk.Label(cont_frame, text="Control Group Column:").grid(row=0, column=0, padx=5)
        control_col_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else "")
        ttk.Combobox(cont_frame, textvariable=control_col_var, values=numeric_cols, width=20).grid(row=0, column=1)
        
        ttk.Label(cont_frame, text="Treatment Group Column:").grid(row=1, column=0, padx=5)
        treatment_col_var = tk.StringVar(value=numeric_cols[1] if len(numeric_cols) > 1 else "")
        ttk.Combobox(cont_frame, textvariable=treatment_col_var, values=numeric_cols, width=20).grid(row=1, column=1)
        
        result_text = scrolledtext.ScrolledText(dialog, height=12, width=80)
        result_text.pack(pady=10)
        
        def run_ab_test():
            from analysis.statistical_tests import ABTesting
            
            try:
                result_text.delete(1.0, tk.END)
                
                if test_type.get() == "conversion":
                    control_conv = int(control_conv_var.get())
                    control_total = int(control_total_var.get())
                    treatment_conv = int(treatment_conv_var.get())
                    treatment_total = int(treatment_total_var.get())
                    
                    result = ABTesting.ab_test_conversion(control_conv, control_total, 
                                                         treatment_conv, treatment_total)
                    
                    result_text.insert(tk.END, "A/B TEST RESULTS - Conversion Rate\n")
                    result_text.insert(tk.END, "=" * 70 + "\n\n")
                    result_text.insert(tk.END, f"Control Rate: {result['control_rate']:.2%}\n")
                    result_text.insert(tk.END, f"Treatment Rate: {result['treatment_rate']:.2%}\n")
                    result_text.insert(tk.END, f"Lift: {result['lift_percentage']:.2f}%\n\n")
                    result_text.insert(tk.END, f"P-value: {result['p_value']:.4f}\n")
                    result_text.insert(tk.END, f"Significant: {'YES' if result['significant'] else 'NO'}\n")
                    result_text.insert(tk.END, f"Winner: {result['winner']}\n\n")
                    result_text.insert(tk.END, f"📊 {result['interpretation']}")
                
                else:  # continuous
                    control_col = control_col_var.get()
                    treatment_col = treatment_col_var.get()
                    
                    if control_col not in self.df.columns or treatment_col not in self.df.columns:
                        messagebox.showerror("Error", "Please select valid columns")
                        return
                    
                    result = ABTesting.ab_test_continuous(self.df[control_col], self.df[treatment_col])
                    
                    result_text.insert(tk.END, "A/B TEST RESULTS - Continuous Metric\n")
                    result_text.insert(tk.END, "=" * 70 + "\n\n")
                    result_text.insert(tk.END, f"Control Mean: {result['control_mean']:.2f}\n")
                    result_text.insert(tk.END, f"Treatment Mean: {result['treatment_mean']:.2f}\n")
                    result_text.insert(tk.END, f"Lift: {result['lift_percentage']:.2f}%\n\n")
                    result_text.insert(tk.END, f"P-value: {result['p_value']:.4f}\n")
                    result_text.insert(tk.END, f"Cohen's d: {result['cohens_d']:.3f} ({result['effect_size']} effect)\n")
                    result_text.insert(tk.END, f"Significant: {'YES' if result['significant'] else 'NO'}\n")
                    result_text.insert(tk.END, f"Winner: {result['winner']}\n\n")
                    result_text.insert(tk.END, f"📊 {result['interpretation']}")
                
            except Exception as e:
                messagebox.showerror("Error", f"A/B test failed: {str(e)}")
        
        ttk.Button(dialog, text="Run A/B Test", command=run_ab_test).pack(pady=10)
    
    def generate_executive_report(self):
        """Generate professional HTML executive report"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        from data_ops.report_generator import ReportGenerator
        
        file_path = filedialog.asksaveasfilename(
            title="Save Executive Report",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                success, report_path = ReportGenerator.generate_executive_summary(self.df, file_path)
                if success:
                    messagebox.showinfo("Success", f"Executive report generated!\n\n{report_path}\n\nOpen in browser to view.")
                    self.update_status("✓ Executive report generated")
                    # Try to open in browser
                    import webbrowser
                    webbrowser.open(report_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def generate_quick_summary(self):
        """Generate quick text summary"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        from data_ops.report_generator import ReportGenerator
        
        summary = ReportGenerator.generate_quick_summary_text(self.df)
        
        # Display in output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, summary)
        self.notebook.select(0)
        
        # Also copy to clipboard
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(summary)
            messagebox.showinfo("Success", "Quick summary generated and copied to clipboard!\n\nPaste into your document or email.")
        except:
            messagebox.showinfo("Success", "Quick summary generated!\n\nUse Copy button to copy to clipboard.")
        
        self.update_status("✓ Quick summary generated")
    
    def format_for_email(self):
        """Format data summary for email"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        from data_ops.report_generator import EmailReportFormatter
        
        email_body = EmailReportFormatter.format_for_email(self.df)
        
        # Display in output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, email_body)
        self.notebook.select(0)
        
        # Copy to clipboard
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(email_body)
            messagebox.showinfo("Success", "Email format generated and copied to clipboard!\n\nPaste directly into your email.")
            self.update_status("✓ Email format ready")
        except:
            messagebox.showinfo("Success", "Email format generated!")
    
    def show_guide(self):
        """Show quick start guide"""
        guide = """QUICK START GUIDE
        
1. Import Data: File > Import CSV/Excel
2. View Data: Click 'View Data' or press Ctrl+D
3. Clean Data: Use Clean menu options
4. Analyze: Use Analysis menu for insights
5. Visualize: Create charts from Visualize menu
6. Export: File > Export to save results

For Shopify Analysis:
- Use Time Series Analysis for sales trends
- Use E-commerce Dashboard for quick insights
- Group By Analysis for customer segmentation
"""
        messagebox.showinfo("Quick Start Guide", guide)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = """KEYBOARD SHORTCUTS
        
Ctrl+O - Import CSV
Ctrl+D - View Data
Ctrl+S - Show Statistics

Coming Soon:
Ctrl+F - Filter Data
Ctrl+E - Export Data
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        about_text = """Professional Data Analysis Tool v2.0 - Shopify Edition

Created for E-commerce & Shopify Data Analysts

✨ Features:
• Data Import/Export (CSV, Excel, JSON)
• Advanced Data Cleaning
• Statistical Analysis
• Time Series Analysis
• E-commerce Dashboard
• 10+ Visualization Types
• Interactive Charts with Zoom/Pan

🎯 Perfect for analyzing:
- Sales trends
- Customer behavior
- Product performance
- Revenue metrics

© 2025 - Built with Python, Pandas, Matplotlib"""
        
        messagebox.showinfo("About", about_text)


# Entry point moved to src/main.py following SEPARATION OF CONCERNS principle
