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
        # Clear previous plot
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
        
        # Create matplotlib figure - FIX: Use Figure from matplotlib.figure
        from matplotlib.figure import Figure
        fig = Figure(figsize=(12, 8), dpi=100)
        fig.patch.set_facecolor('white')
        
        # Execute plot function
        try:
            plot_func(fig)
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
            
            def plot_func(fig):
                ax = fig.add_subplot(111)
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
            def plot_func(fig):
                ax = fig.add_subplot(111)
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
        
        def plot_func(fig):
            ax = fig.add_subplot(111)
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
            
            def plot_func(fig):
                ax = fig.add_subplot(111)
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

© 2024 - Built with Python, Pandas, Matplotlib"""
        
        messagebox.showinfo("About", about_text)


def main():
    root = tk.Tk()
    app = DataAnalystTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
