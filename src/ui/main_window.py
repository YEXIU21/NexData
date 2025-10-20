"""
Professional Data Analysis Tool
A comprehensive tool for data analysts with data import, cleaning, analysis, and visualization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
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

# Import theme manager
from ui.theme_manager import ThemeManager

# Import Excel pivot exporter
from data_ops.excel_pivot_export import ExcelPivotExporter

# Import API connector window
from ui.api_connector_window import APIConnectorWindow
from data_ops.data_manager import get_data_manager

# Import progress window for long operations
from ui.progress_window import run_with_progress, ProgressWindow

# Import tooltip system
from ui.tooltip import create_tooltip, COMMON_TOOLTIPS

# Import autosave manager
from utils.autosave_manager import get_autosave_manager

# Import service layer
from services import CleaningService, AnalysisService, AIService, DataService

# Import UI managers
from ui.managers import MenuManager, ExportManager, VisualizationManager

# Import dialogs
from ui.dialogs import CleaningDialogs
from .dialogs.visualization_dialogs import VisualizationDialogs
from .dialogs.analysis_dialogs import AnalysisDialogs


class DataAnalystApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NexData - Professional Data Analysis Tool")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        self.df = None
        self.original_df = None
        self.file_path = None
        
        # Enterprise-grade data manager
        self.data_manager = get_data_manager()
        self.use_smart_loading = True  # Toggle for enterprise features
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.root)
        
        # Initialize performance monitor
        from utils.performance_monitor import PerformanceMonitor
        self.perf_monitor = PerformanceMonitor()
        
        # Initialize service layer
        self.cleaning_service = CleaningService()
        self.analysis_service = AnalysisService()
        self.ai_service = AIService()
        self.data_service = DataService()
        
        # Initialize autosave (5 minute interval)
        self.autosave_manager = get_autosave_manager(save_interval=300)
        
        # Initialize UI managers
        self.menu_manager = MenuManager(self.root, self)
        self.export_manager = ExportManager(self)
        self.viz_manager = VisualizationManager(self)
        
        self.setup_styles()
        self.create_menu()
        self.create_ui()
        self.setup_keyboard_shortcuts()
        self.check_recovery_data()
        
        # Apply default system theme
        self.theme_manager.apply_theme('system')
        
        self.update_status("Ready | Auto-save: ON")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        # Note: Styles will be configured by theme_manager
        # Initial setup for fonts only, colors handled by theme
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10, 'bold'), padding=5)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common operations"""
        # File operations
        self.root.bind('<Control-o>', lambda e: self.import_csv())
        self.root.bind('<Control-O>', lambda e: self.import_csv())
        self.root.bind('<Control-e>', lambda e: self.export_csv())
        self.root.bind('<Control-E>', lambda e: self.export_csv())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())
        
        # Data operations
        self.root.bind('<Control-d>', lambda e: self.view_data())
        self.root.bind('<Control-D>', lambda e: self.view_data())
        self.root.bind('<Control-s>', lambda e: self.show_statistics())
        self.root.bind('<Control-S>', lambda e: self.show_statistics())
        self.root.bind('<Control-r>', lambda e: self.reset_data())
        self.root.bind('<Control-R>', lambda e: self.reset_data())
        self.root.bind('<Control-f>', lambda e: self.advanced_filters())
        self.root.bind('<Control-F>', lambda e: self.advanced_filters())
        
        # Help
        self.root.bind('<F1>', lambda e: self.show_about())
        
        self.update_status("Keyboard shortcuts enabled")
    
    def check_recovery_data(self):
        """Check for crash recovery data on startup"""
        if self.autosave_manager.has_recovery_data():
            recovery_info = self.autosave_manager.get_recovery_info()
            if recovery_info:
                message = f"""Auto-saved data found!

Last saved: {recovery_info['timestamp']}
Rows: {recovery_info['rows']}
Columns: {recovery_info['columns']}
Size: {recovery_info['size_mb']:.2f} MB

Would you like to recover this data?"""
                
                response = messagebox.askyesno("Crash Recovery", message)
                if response:
                    df = self.autosave_manager.recover_data()
                    if df is not None:
                        self.df = df
                        self.original_df = df.copy()
                        self.file_path = recovery_info.get('original_path')
                        self.update_info_panel()
                        self.view_data()
                        messagebox.showinfo("Success", "Data recovered successfully!")
                        self.update_status("Recovered from auto-save")
                    else:
                        messagebox.showerror("Error", "Failed to recover data")
                else:
                    # User declined recovery, clear old data
                    self.autosave_manager.clear_recovery_data()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Import Excel", command=self.import_excel)
        file_menu.add_command(label="Connect to API", command=self.open_api_connector)
        file_menu.add_separator()
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_command(label="Export Excel", command=self.export_excel)
        file_menu.add_command(label="Export Excel with Pivot", command=self.export_excel_with_pivot)
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Generate Executive Report (HTML)", command=self.generate_executive_report)
        file_menu.add_command(label="Generate Quick Summary", command=self.generate_quick_summary)
        file_menu.add_command(label="Format for Email", command=self.format_for_email)
        file_menu.add_command(label="Export to PowerPoint", command=self.export_powerpoint)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Data", menu=data_menu)
        data_menu.add_command(label="View Data", command=self.view_data)
        data_menu.add_command(label="Data Info", command=self.show_data_info)
        data_menu.add_command(label="Statistics", command=self.show_statistics)
        data_menu.add_separator()
        data_menu.add_command(label="Sort Data", command=self.sort_data)
        data_menu.add_command(label="Convert Data Types", command=self.convert_dtypes)
        data_menu.add_separator()
        data_menu.add_command(label="Advanced Filters", command=self.advanced_filters)
        data_menu.add_command(label="Data Quality Check", command=self.data_quality_check)
        data_menu.add_separator()
        data_menu.add_command(label="Reset Data", command=self.reset_data)
        
        clean_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Clean", menu=clean_menu)
        clean_menu.add_command(label="🤖 Data Quality Advisor", command=self.data_quality_advisor)
        clean_menu.add_separator()
        clean_menu.add_command(label="Remove Duplicates", command=self.remove_duplicates)
        clean_menu.add_command(label="Handle Missing Values", command=self.handle_missing_values)
        clean_menu.add_command(label="Smart Fill Missing Data", command=self.smart_fill_missing)
        clean_menu.add_separator()
        clean_menu.add_command(label="Find & Replace", command=self.find_replace)
        clean_menu.add_command(label="Standardize Text Case", command=self.standardize_text_case)
        clean_menu.add_command(label="Remove Empty Rows/Columns", command=self.remove_empty)
        clean_menu.add_command(label="Trim All Columns", command=self.trim_all_columns)
        clean_menu.add_separator()
        clean_menu.add_command(label="Remove Outliers", command=self.remove_outliers)
        clean_menu.add_command(label="Clean Order IDs", command=self.clean_order_ids)
        clean_menu.add_separator()
        clean_menu.add_command(label="Data Type Converter", command=self.convert_data_types)
        clean_menu.add_command(label="Standardize Dates", command=self.standardize_dates)
        clean_menu.add_command(label="Remove Special Characters", command=self.remove_special_chars)
        clean_menu.add_command(label="Split/Merge Columns", command=self.split_merge_columns)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="🤖 AI Report Generator", command=self.ai_report_generator)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Group By Analysis", command=self.groupby_analysis)
        analysis_menu.add_command(label="Pivot Table", command=self.pivot_table)
        analysis_menu.add_command(label="SQL Query", command=self.sql_query)
        analysis_menu.add_command(label="Data Profiling Report", command=self.data_profiling_report)
        analysis_menu.add_command(label="Auto Insights", command=self.auto_insights)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Column Analysis", command=self.column_analysis)
        analysis_menu.add_command(label="Correlation Analysis", command=self.correlation_analysis)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Statistical Tests", command=self.statistical_tests)
        analysis_menu.add_command(label="A/B Testing", command=self.ab_testing)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="RFM Customer Segmentation", command=self.rfm_segmentation)
        analysis_menu.add_command(label="Time Series Forecasting", command=self.time_series_forecasting)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Sales Dashboard", command=self.sales_dashboard)
        analysis_menu.add_command(label="Customer Dashboard", command=self.customer_dashboard)
        analysis_menu.add_command(label="E-commerce Dashboard", command=self.ecommerce_dashboard)
        
        viz_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualize", menu=viz_menu)
        viz_menu.add_command(label="Bar Chart", command=self.plot_bar)
        viz_menu.add_command(label="Line Chart", command=self.plot_line)
        viz_menu.add_command(label="Pie Chart", command=self.plot_pie)
        viz_menu.add_separator()
        viz_menu.add_command(label="Histogram", command=self.plot_histogram)
        viz_menu.add_command(label="Box Plot", command=self.plot_boxplot)
        viz_menu.add_command(label="Scatter Plot", command=self.plot_scatter)
        viz_menu.add_separator()
        viz_menu.add_command(label="Distribution Plot (KDE)", command=self.plot_distribution)
        viz_menu.add_command(label="Violin Plot", command=self.plot_violin)
        viz_menu.add_command(label="Correlation Heatmap", command=self.plot_heatmap)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Compare Datasets", command=self.compare_datasets)
        
        # View menu for themes
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="System Default", command=lambda: self.change_theme('system'))
        theme_menu.add_command(label="Light Mode", command=lambda: self.change_theme('light'))
        theme_menu.add_command(label="Dark Mode", command=lambda: self.change_theme('dark'))
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide & Tutorials", command=self.show_user_guide)
        help_menu.add_command(label="Quick Start Guide", command=self.show_quick_start)
        help_menu.add_separator()
        help_menu.add_command(label="Performance Monitor", command=self.performance_monitor)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_ui(self):
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(title_frame, text="NexData - Professional Data Analysis", style='Title.TLabel').pack()
        
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel
        left_panel = ttk.Frame(self.main_paned, relief=tk.RIDGE, borderwidth=2)
        self.main_paned.add(left_panel, weight=1)
        
        ttk.Label(left_panel, text="Quick Actions", style='Header.TLabel').pack(pady=10)
        
        actions_frame = ttk.Frame(left_panel)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create buttons with tooltips
        btn_import_csv = ttk.Button(actions_frame, text="Import CSV", command=self.import_csv, style='Action.TButton')
        btn_import_csv.pack(fill=tk.X, pady=2)
        create_tooltip(btn_import_csv, COMMON_TOOLTIPS['import_csv'])
        
        btn_import_excel = ttk.Button(actions_frame, text="Import Excel", command=self.import_excel, style='Action.TButton')
        btn_import_excel.pack(fill=tk.X, pady=2)
        create_tooltip(btn_import_excel, COMMON_TOOLTIPS['import_excel'])
        
        btn_view = ttk.Button(actions_frame, text="View Data", command=self.view_data, style='Action.TButton')
        btn_view.pack(fill=tk.X, pady=2)
        create_tooltip(btn_view, COMMON_TOOLTIPS['view_data'])
        
        btn_stats = ttk.Button(actions_frame, text="Statistics", command=self.show_statistics, style='Action.TButton')
        btn_stats.pack(fill=tk.X, pady=2)
        create_tooltip(btn_stats, COMMON_TOOLTIPS['statistics'])
        
        btn_reset = ttk.Button(actions_frame, text="Reset Data", command=self.reset_data, style='Action.TButton')
        btn_reset.pack(fill=tk.X, pady=2)
        create_tooltip(btn_reset, COMMON_TOOLTIPS['reset_data'])
        
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
        
        # Create PanedWindow for split view
        output_paned = ttk.PanedWindow(output_frame, orient=tk.VERTICAL)
        output_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text output (for logs/messages)
        text_frame = ttk.LabelFrame(output_paned, text="Messages & Logs", padding=5)
        self.output_text = scrolledtext.ScrolledText(text_frame, height=8, font=('Courier', 9), wrap=tk.NONE)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        output_paned.add(text_frame, weight=1)
        
        # Grid output (for table results) - Excel-like
        grid_frame = ttk.LabelFrame(output_paned, text="Results Grid (Excel-like)", padding=5)
        
        # Create Treeview with scrollbars for grid display
        tree_scroll_frame = ttk.Frame(grid_frame)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_yscroll = ttk.Scrollbar(tree_scroll_frame, orient=tk.VERTICAL)
        tree_xscroll = ttk.Scrollbar(tree_scroll_frame, orient=tk.HORIZONTAL)
        
        self.output_grid = ttk.Treeview(
            tree_scroll_frame,
            yscrollcommand=tree_yscroll.set,
            xscrollcommand=tree_xscroll.set,
            show='tree headings',
            selectmode='extended'
        )
        
        tree_yscroll.config(command=self.output_grid.yview)
        tree_xscroll.config(command=self.output_grid.xview)
        
        self.output_grid.grid(row=0, column=0, sticky='nsew')
        tree_yscroll.grid(row=0, column=1, sticky='ns')
        tree_xscroll.grid(row=1, column=0, sticky='ew')
        
        tree_scroll_frame.grid_rowconfigure(0, weight=1)
        tree_scroll_frame.grid_columnconfigure(0, weight=1)
        
        output_paned.add(grid_frame, weight=2)
        
        # Initialize grid as empty
        self.output_grid['columns'] = ()
        self.output_grid.heading('#0', text='#')
        self.output_grid.column('#0', width=50, anchor='center')
        
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
        
    def update_autosave_data(self):
        """Update autosave manager with current dataframe after modifications"""
        if self.df is not None:
            self.autosave_manager.update_data(self.df)
    
    def update_info_panel(self):
        """Update info panel with dataset information - Enterprise Edition"""
        self.info_text.delete(1.0, tk.END)
        
        if self.df is None:
            self.info_text.insert(tk.END, "No data loaded.\n\nUse File menu to import:\n- CSV files\n- Excel files\n- API data (Shopify, etc.)")
        else:
            # Get metadata from data manager if using smart loading
            metadata = {}
            if self.use_smart_loading:
                metadata = self.data_manager.get_metadata()
            
            # File/Source info
            source = os.path.basename(self.file_path) if self.file_path else metadata.get('source', 'API')
            info = f"📊 Dataset Info\n{'='*40}\n\n"
            info += f"Source: {source}\n"
            
            # Storage mode (Enterprise feature)
            storage_mode = metadata.get('storage', 'memory')
            if storage_mode == 'database':
                total_rows = metadata.get('rows', 0)
                info += f"💾 Storage: Database (Large Dataset)\n"
                info += f"📈 Total Rows: {total_rows:,}\n"
                info += f"👁️ Viewing: Sample of {len(self.df):,} rows\n"
                info += f"Columns: {metadata.get('cols', 0)}\n\n"
                info += "ℹ️ Using on-demand loading for optimal performance.\n"
                info += "Data is paginated automatically.\n\n"
            else:
                info += f"💾 Storage: Memory (Fast Mode)\n"
                info += f"Shape: {self.df.shape[0]:,} rows × {self.df.shape[1]} columns\n\n"
            
            # Column info
            info += f"Columns:\n"
            for col in self.df.columns[:15]:
                info += f"  • {col} ({self.df[col].dtype})\n"
            if len(self.df.columns) > 15:
                info += f"  ... and {len(self.df.columns) - 15} more\n"
            
            # Data quality info
            missing = self.df.isnull().sum().sum()
            if missing > 0:
                info += f"\n⚠️ Missing Values: {missing}\n"
            else:
                info += f"\n✅ No Missing Values\n"
            
            # Size info
            if 'size_mb' in metadata:
                info += f"💿 Size: {metadata['size_mb']:.2f} MB\n"
            
            self.info_text.insert(tk.END, info)
    
    def display_results_in_grid(self, data, title="Results"):
        """
        Display data in Excel-like grid format in Output tab.
        
        Args:
            data: Can be pandas DataFrame, Series, or dict
            title: Title for the results
        """
        # Clear existing grid
        for item in self.output_grid.get_children():
            self.output_grid.delete(item)
        
        # Convert data to DataFrame if needed
        if isinstance(data, dict):
            df = pd.DataFrame(list(data.items()), columns=['Key', 'Value'])
        elif isinstance(data, pd.Series):
            df = pd.DataFrame({data.name or 'Value': data}).reset_index()
            df.columns = ['Index', data.name or 'Value']
        elif isinstance(data, pd.DataFrame):
            df = data.reset_index(drop=False) if data.index.name else data
        else:
            # Fallback to text display
            self.output_text.insert(tk.END, f"\n{title}:\n{str(data)}\n")
            return
        
        # Configure columns
        columns = list(df.columns)
        self.output_grid['columns'] = columns
        
        # Set column headings and widths
        self.output_grid.heading('#0', text='#', anchor='center')
        self.output_grid.column('#0', width=50, anchor='center', stretch=False)
        
        for col in columns:
            self.output_grid.heading(col, text=col, anchor='w')
            # Auto-size columns based on content
            max_width = max(len(str(col)) * 10, 100)
            if len(df) > 0:
                max_content = df[col].astype(str).str.len().max()
                max_width = min(max(max_width, max_content * 8), 300)
            self.output_grid.column(col, width=max_width, anchor='w')
        
        # Insert data rows
        for idx, row in df.iterrows():
            values = []
            for col in columns:
                val = row[col]
                # Format numbers nicely
                if pd.api.types.is_float_dtype(type(val)) and not pd.isna(val):
                    values.append(f"{val:,.2f}")
                elif pd.api.types.is_integer_dtype(type(val)) and not pd.isna(val):
                    values.append(f"{val:,}")
                else:
                    values.append(str(val))
            
            self.output_grid.insert('', 'end', text=str(idx + 1), values=values)
        
        # Add row count to status
        self.output_text.insert(tk.END, f"\n{title}: {len(df)} rows displayed in grid\n")
    
    def import_csv(self):
        file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                # Check file size for progress bar
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                if file_size_mb > 10:  # Show progress for files > 10MB
                    # Use progress window for large files
                    def load_task(progress):
                        progress(10, "Opening file...", f"File size: {file_size_mb:.1f}MB")
                        df = self.data_service.import_csv(file_path)
                        progress(80, "Processing data...", f"Loaded {len(df)} rows")
                        progress(100, "Complete!", f"{len(df)} rows, {len(df.columns)} columns")
                        return df
                    
                    self.df = run_with_progress(self.root, load_task, "Importing Large CSV", cancelable=False)
                else:
                    # Direct import for small files
                    self.df = self.data_service.import_csv(file_path)
                
                self.original_df = self.df.copy()
                self.file_path = file_path
                self.update_status(f"Loaded: {os.path.basename(file_path)}")
                self.update_info_panel()
                self.view_data()
                
                # Start autosave
                self.autosave_manager.start(self.df, file_path)
                
                messagebox.showinfo("Success", f"CSV loaded!\n{self.df.shape[0]} rows, {self.df.shape[1]} cols\n\nAuto-save: ACTIVE")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")
    
    def import_excel(self):
        file_path = filedialog.askopenfilename(title="Select Excel file", filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")])
        if file_path:
            try:
                # Check file size for progress bar
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                if file_size_mb > 5:  # Show progress for files > 5MB (Excel is heavier)
                    # Use progress window for large files
                    def load_task(progress):
                        progress(10, "Opening Excel file...", f"File size: {file_size_mb:.1f}MB")
                        df = self.data_service.import_excel(file_path)
                        progress(80, "Processing sheets...", f"Loaded {len(df)} rows")
                        progress(100, "Complete!", f"{len(df)} rows, {len(df.columns)} columns")
                        return df
                    
                    self.df = run_with_progress(self.root, load_task, "Importing Large Excel", cancelable=False)
                else:
                    # Direct import for small files
                    self.df = self.data_service.import_excel(file_path)
                
                self.original_df = self.df.copy()
                self.file_path = file_path
                self.update_status(f"Loaded: {os.path.basename(file_path)}")
                self.update_info_panel()
                self.view_data()
                
                # Start autosave
                self.autosave_manager.start(self.df, file_path)
                
                messagebox.showinfo("Success", f"Excel loaded!\n{self.df.shape[0]} rows, {self.df.shape[1]} cols\n\nAuto-save: ACTIVE")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Excel:\n{str(e)}")
    
    def open_api_connector(self):
        """Open API Connector window"""
        def load_api_data(df):
            """Callback to load data from API into main app - Enterprise Edition"""
            if self.use_smart_loading:
                # Use intelligent data manager
                success, message = self.data_manager.load_data(df, source_name="api_data")
                
                if success:
                    # For UI compatibility, keep reference to sample data
                    self.df = self.data_manager.get_sample(1000)  # Keep 1K rows for UI
                    self.original_df = self.df.copy()
                    self.file_path = None
                    
                    # Show storage mode in status
                    metadata = self.data_manager.get_metadata()
                    storage_mode = metadata.get('storage', 'unknown')
                    self.update_status(f"Loaded from API: {len(df)} rows ({storage_mode} mode)")
                    self.update_info_panel()
                    self.view_data()
                    
                    # Info message about storage
                    if storage_mode == 'database':
                        messagebox.showinfo("Large Dataset", 
                            f"{message}\n\n"
                            "✅ Using database storage for optimal performance!\n"
                            "Data is loaded on-demand with pagination.")
                else:
                    messagebox.showerror("Error", f"Failed to load data: {message}")
            else:
                # Traditional in-memory loading
                self.df = df
                self.original_df = df.copy()
                self.file_path = None
                self.update_status(f"Loaded from API: {len(df)} rows")
                self.update_info_panel()
                self.view_data()
        
        APIConnectorWindow(self.root, load_api_data)
    
    def export_csv(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                # Use data service
                self.data_service.export_csv(self.df, file_path)
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
                # Use data service
                self.data_service.export_excel(self.df, file_path)
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
                self.update_status(f"Exported to Excel")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_json(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                # Use data service
                self.data_service.export_json(self.df, file_path)
                messagebox.showinfo("Success", f"Exported to:\n{file_path}")
                self.update_status(f"Exported to JSON")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_excel_with_pivot(self):
        """Export Excel with pivot table configuration dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        # Create configuration dialog
        pivot_window = tk.Toplevel(self.root)
        pivot_window.title("Export Excel with Pivot Table")
        pivot_window.geometry("500x450")
        pivot_window.transient(self.root)
        pivot_window.grab_set()
        
        # Title
        ttk.Label(pivot_window, text="Configure Pivot Table Export", style='Header.TLabel').pack(pady=10)
        
        # Frame for configuration
        config_frame = ttk.Frame(pivot_window, padding=20)
        config_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get column names
        columns = list(self.df.columns)
        
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
        numeric_columns = list(self.df.select_dtypes(include=['number']).columns)
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
                        self.df, file_path, pivot_config, chart_type='bar'
                    )
                else:
                    success, message = ExcelPivotExporter.export_with_pivot(
                        self.df, file_path, pivot_config
                    )
                
                if success:
                    messagebox.showinfo("Success", message, parent=pivot_window)
                    self.update_status("Exported Excel with pivot table")
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
    
    def view_data(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"=== DATA VIEW (First 100 rows) ===\n\n")
        self.output_text.update_idletasks()  # Show header
        self.output_text.insert(tk.END, f"{self.df.head(100).to_string()}")
        self.output_text.update_idletasks()  # Show data
        self.notebook.select(0)
        self.update_status("Displaying data")
    
    def show_data_info(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=== DATA INFORMATION ===\n\n")
        self.output_text.update_idletasks()  # Show header
        
        info_str = f"Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns\n\n"
        for col in self.df.columns:
            non_null = self.df[col].notna().sum()
            null_count = self.df[col].isna().sum()
            info_str += f"{col}: {self.df[col].dtype} | Non-Null: {non_null} | Null: {null_count} | Unique: {self.df[col].nunique()}\n"
        
        self.output_text.insert(tk.END, info_str)
        self.output_text.update_idletasks()  # Show info
        self.notebook.select(0)
        self.update_status("Data information displayed")
    
    def show_statistics(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Get statistics using pandas describe (comprehensive view)
        stats_df = self.df.describe()
        
        # Display header in text
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "STATISTICAL SUMMARY\n")
        self.output_text.insert(tk.END, f"Numeric Columns: {len(stats_df.columns)}\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.update_idletasks()
        
        # Display statistics in Excel-like grid
        self.display_results_in_grid(stats_df, title="Statistical Summary")
        
        self.notebook.select(0)
        self.update_status("Statistics displayed in grid format")
    
    def reset_data(self):
        if self.original_df is None:
            messagebox.showwarning("Warning", "No original data!")
            return
        if messagebox.askyesno("Confirm", "Reset to original data? This will clear all filters and modifications."):
            filtered_count = len(self.df)
            self.df = self.original_df.copy()
            self.update_autosave_data()
            original_count = len(self.df)
            
            # Show clear output message
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            self.output_text.insert(tk.END, "DATA RESET - FILTERS CLEARED\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n\n")
            self.output_text.insert(tk.END, f"✓ Filtered data had: {filtered_count} rows\n")
            self.output_text.insert(tk.END, f"✓ Original data restored: {original_count} rows\n")
            self.output_text.insert(tk.END, f"✓ All filters and modifications cleared\n\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            self.output_text.insert(tk.END, "SUCCESS: Full dataset restored!\n")
            self.output_text.update_idletasks()
            self.notebook.select(0)  # Switch to Output tab
            
            self.update_info_panel()
            self.view_data()
            self.update_status("Data reset - all filters cleared")
            messagebox.showinfo("Success", f"Data reset complete!\n\nRestored {original_count} rows")
    
    def remove_duplicates(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, removed, status_msg, subset_cols, keep_option):
            """Callback when duplicates removed"""
            before = len(self.df)
            self.df = cleaned_df
            self.update_autosave_data()
            
            # Output to text area
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            self.output_text.insert(tk.END, "REMOVE DUPLICATES - OPERATION COMPLETE\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n\n")
            self.output_text.insert(tk.END, f"✓ Original rows: {before}\n")
            self.output_text.insert(tk.END, f"✓ Duplicates removed: {removed}\n")
            self.output_text.insert(tk.END, f"✓ Remaining rows: {len(self.df)}\n\n")
            self.output_text.insert(tk.END, f"Columns checked: {', '.join(subset_cols)}\n")
            self.output_text.insert(tk.END, f"Keep strategy: {keep_option}\n\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            if removed > 0:
                self.output_text.insert(tk.END, f"SUCCESS: {removed} duplicate row(s) removed from dataset\n")
            else:
                self.output_text.insert(tk.END, "INFO: No duplicates found in selected columns\n")
            self.output_text.update_idletasks()
            self.notebook.select(0)
            
            self.update_info_panel()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_remove_duplicates_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def remove_duplicates_OLD(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # OLD CODE - TO BE REMOVED
        # Create dialog for duplicate removal options
        dialog = tk.Toplevel(self.root)
        dialog.title("Remove Duplicates")
        dialog.geometry("500x450")
        
        ttk.Label(dialog, text="Remove Duplicate Rows", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Check for duplicates first
        all_duplicates = self.df.duplicated(keep=False).sum()
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
        for col in self.df.columns:
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
            dup_mask = self.df.duplicated(subset=subset_cols, keep=keep_option)
            duplicates = self.df[dup_mask]
            
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
            
            before = len(self.df)
            try:
                # Use cleaning service
                cleaned_df, removed = self.cleaning_service.remove_duplicates(
                    self.df, 
                    subset=subset_cols, 
                    keep=keep_option
                )
                self.df = cleaned_df
                self.update_autosave_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove duplicates: {str(e)}")
                return
            
            # Output to text area
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            self.output_text.insert(tk.END, "REMOVE DUPLICATES - OPERATION COMPLETE\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n\n")
            self.output_text.insert(tk.END, f"✓ Original rows: {before}\n")
            self.output_text.insert(tk.END, f"✓ Duplicates removed: {removed}\n")
            self.output_text.insert(tk.END, f"✓ Remaining rows: {len(self.df)}\n\n")
            self.output_text.insert(tk.END, f"Columns checked: {', '.join(subset_cols)}\n")
            self.output_text.insert(tk.END, f"Keep strategy: {keep_option}\n\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            if removed > 0:
                self.output_text.insert(tk.END, f"SUCCESS: {removed} duplicate row(s) removed from dataset\n")
            else:
                self.output_text.insert(tk.END, "INFO: No duplicates found in selected columns\n")
            self.output_text.update_idletasks()
            self.notebook.select(0)  # Switch to Output tab
            
            self.update_info_panel()
            self.update_status(f"Removed {removed} duplicates")
            messagebox.showinfo("Success", 
                              f"Removed {removed} duplicate rows\n\n"
                              f"Based on columns: {', '.join(subset_cols)}\n"
                              f"Keep strategy: {keep_option}")
            dialog.destroy()
        
        ttk.Button(action_frame, text="Preview", command=preview_duplicates).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Remove Duplicates", command=remove, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def handle_missing_values(self):
        """Handle missing values - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, method, selected_col, status_msg, custom_val=None):
            """Callback when missing values handled"""
            self.df = cleaned_df
            self.update_autosave_data()
            
            # Output to text area
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            self.output_text.insert(tk.END, "HANDLE MISSING VALUES - OPERATION COMPLETE\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n\n")
            self.output_text.insert(tk.END, f"Method applied: {method.upper()}\n")
            self.output_text.insert(tk.END, f"Target: {selected_col}\n")
            if custom_val:
                self.output_text.insert(tk.END, f"Custom value: {custom_val}\n")
            self.output_text.insert(tk.END, f"\n✓ Current missing values in dataset: {self.df.isnull().sum().sum()}\n")
            self.output_text.insert(tk.END, f"✓ Total rows: {len(self.df)}\n\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            self.output_text.insert(tk.END, f"SUCCESS: Missing values handled using {method} method\n")
            self.output_text.update_idletasks()
            self.notebook.select(0)
            
            self.update_info_panel()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_handle_missing_dialog(
            self.root, self.df, on_complete
        )
    
    def remove_outliers(self):
        """Remove outliers from numeric columns - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, removed, status_msg, details):
            """Callback when outliers removed"""
            before = len(self.df)
            self.df = cleaned_df
            self.update_autosave_data()
            
            # Output to text area
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            self.output_text.insert(tk.END, "REMOVE OUTLIERS - OPERATION COMPLETE\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n\n")
            self.output_text.insert(tk.END, f"Column analyzed: {details['column']}\n")
            self.output_text.insert(tk.END, f"Detection method: {details['method']}\n\n")
            self.output_text.insert(tk.END, f"✓ Original rows: {before}\n")
            self.output_text.insert(tk.END, f"✓ Outliers removed: {removed}\n")
            self.output_text.insert(tk.END, f"✓ Remaining rows: {len(self.df)}\n\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            if removed > 0:
                self.output_text.insert(tk.END, f"SUCCESS: {removed} outlier row(s) removed from dataset\n")
            else:
                self.output_text.insert(tk.END, "INFO: No outliers detected with current settings\n")
            self.output_text.update_idletasks()
            self.notebook.select(0)
            
            self.update_info_panel()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_remove_outliers_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def clean_order_ids(self):
        """Clean Order IDs by removing letter suffixes - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, col, affected_count, status_msg, output_msg):
            """Callback when Order IDs cleaned"""
            self.df = cleaned_df
            self.update_autosave_data()
            
            # Display output
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, output_msg)
            self.output_text.update_idletasks()
            self.notebook.select(0)  # Switch to Output tab
            
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_clean_order_ids_dialog(
            self.root, self.df, on_complete
        )
    
    def smart_fill_missing(self):
        """Smart fill missing values by looking up matching IDs - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, filled_count, status_msg, details):
            """Callback when smart fill complete"""
            self.df = cleaned_df
            self.update_autosave_data()
            
            # Output results
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            self.output_text.insert(tk.END, "SMART FILL MISSING DATA - COMPLETE\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n\n")
            self.output_text.insert(tk.END, f"Target column: {details['target_column']}\n")
            self.output_text.insert(tk.END, f"Lookup key: {details['lookup_key']}\n\n")
            self.output_text.insert(tk.END, f"✓ Missing values before: {details['before']}\n")
            self.output_text.insert(tk.END, f"✓ Values filled: {filled_count}\n")
            self.output_text.insert(tk.END, f"✓ Still missing: {details['still_missing']}\n\n")
            self.output_text.insert(tk.END, "=" * 80 + "\n")
            
            if filled_count > 0:
                self.output_text.insert(tk.END, f"SUCCESS: Filled {filled_count} missing value(s)\n")
                self.output_text.insert(tk.END, f"Example: Found {details['target_column']} by matching {details['lookup_key']}\n")
            else:
                self.output_text.insert(tk.END, "INFO: No values could be filled (no matching keys found)\n")
            
            self.output_text.update_idletasks()
            self.notebook.select(0)
            
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_smart_fill_missing_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def data_quality_advisor(self):
        """AI-powered data quality analysis and recommendations"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Data Quality Advisor - AI Recommendations")
        dialog.geometry("700x600")
        
        ttk.Label(dialog, text="🤖 Data Quality Advisor", font=('Arial', 14, 'bold')).pack(pady=15)
        ttk.Label(dialog, text="Analyzing your data and recommending actions...", font=('Arial', 10)).pack(pady=5)
        
        # Create notebook for categories
        advisor_notebook = ttk.Notebook(dialog)
        advisor_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Analyze data using AI service
        recommendations = self.ai_service.analyze_data_quality(self.df)
        
        # Map tool names to actual action methods
        action_map = {
            'Remove Duplicates': self.remove_duplicates,
            'Smart Fill Missing Data': self.smart_fill_missing,
            'Handle Missing Values': self.handle_missing_values,
            'Trim All Columns': self.trim_all_columns,
            'Standardize Text Case': self.standardize_text_case,
            'Remove Empty Rows/Columns': self.remove_empty,
            'Remove Outliers': self.remove_outliers
        }
        
        # Add action callbacks to recommendations
        for rec in recommendations:
            tool_name = rec['tool']
            rec['action'] = action_map.get(tool_name, lambda: messagebox.showinfo("Info", "Tool coming soon!"))
        
        # Group by priority
        high_priority = [r for r in recommendations if r['priority'] == 'High']
        medium_priority = [r for r in recommendations if r['priority'] == 'Medium']
        low_priority = [r for r in recommendations if r['priority'] == 'Low']
        
        # High Priority Tab
        if high_priority:
            high_frame = ttk.Frame(advisor_notebook)
            advisor_notebook.add(high_frame, text=f"🔴 High Priority ({len(high_priority)})")
            self._create_recommendations_view(high_frame, high_priority, dialog)
        
        # Medium Priority Tab
        if medium_priority:
            med_frame = ttk.Frame(advisor_notebook)
            advisor_notebook.add(med_frame, text=f"🟡 Medium Priority ({len(medium_priority)})")
            self._create_recommendations_view(med_frame, medium_priority, dialog)
        
        # Low Priority Tab
        if low_priority:
            low_frame = ttk.Frame(advisor_notebook)
            advisor_notebook.add(low_frame, text=f"🟢 Low Priority ({len(low_priority)})")
            self._create_recommendations_view(low_frame, low_priority, dialog)
        
        # All Clear Tab
        if not recommendations:
            clear_frame = ttk.Frame(advisor_notebook)
            advisor_notebook.add(clear_frame, text="✅ All Clear")
            ttk.Label(clear_frame, text="✅ No data quality issues detected!", 
                     font=('Arial', 12, 'bold'), foreground='green').pack(pady=50)
            ttk.Label(clear_frame, text="Your data looks clean and ready for analysis!", 
                     font=('Arial', 10)).pack(pady=10)
        
        # Summary at bottom
        summary_frame = ttk.Frame(dialog)
        summary_frame.pack(fill=tk.X, padx=15, pady=10)
        
        summary_text = f"Found {len(recommendations)} issue(s): "
        summary_text += f"{len(high_priority)} High, {len(medium_priority)} Medium, {len(low_priority)} Low"
        ttk.Label(summary_frame, text=summary_text, font=('Arial', 10, 'bold')).pack()
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    # Note: _analyze_data_quality() removed - now handled by AIService.analyze_data_quality()
    
    def _create_recommendations_view(self, parent, recommendations, dialog):
        """Create scrollable view of recommendations"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add recommendations
        for idx, rec in enumerate(recommendations, 1):
            rec_frame = ttk.LabelFrame(scrollable_frame, text=f"Issue #{idx}: {rec['issue']}", padding=10)
            rec_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(rec_frame, text=f"Impact: {rec['impact']}", 
                     font=('Arial', 9), wraplength=550).pack(anchor='w', pady=2)
            
            ttk.Label(rec_frame, text=f"Recommended Tool: {rec['tool']}", 
                     font=('Arial', 9, 'bold'), foreground='blue').pack(anchor='w', pady=2)
            
            def make_action(action, dlg):
                def run_action():
                    dlg.destroy()
                    action()
                return run_action
            
            ttk.Button(rec_frame, text=f"🔧 Fix with {rec['tool']}", 
                      command=make_action(rec['action'], dialog),
                      style='Action.TButton').pack(anchor='w', pady=5)
    
    def ai_report_generator(self):
        """AI-powered automatic report generation"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("AI Report Generator")
        dialog.geometry("800x700")
        
        ttk.Label(dialog, text="🤖 AI Report Generator", font=('Arial', 14, 'bold')).pack(pady=15)
        ttk.Label(dialog, text="Generating comprehensive analysis report...", font=('Arial', 10)).pack(pady=5)
        
        # Report display
        report_frame = ttk.LabelFrame(dialog, text="Generated Report", padding=10)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, font=('Courier', 9))
        report_text.pack(fill=tk.BOTH, expand=True)
        
        # Generate report using AI service
        report_content = self.ai_service.generate_report(self.df)
        report_text.insert(1.0, report_content)
        report_text.config(state=tk.DISABLED)
        
        # Export buttons
        export_frame = ttk.Frame(dialog)
        export_frame.pack(pady=10)
        
        def export_txt():
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                messagebox.showinfo("Success", f"Report exported to:\n{file_path}")
        
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(report_content)
            messagebox.showinfo("Success", "Report copied to clipboard!")
        
        ttk.Button(export_frame, text="📄 Export as TXT", command=export_txt, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📋 Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    # Note: _generate_ai_report(), _generate_key_findings(), and _generate_recommendations() removed
    # These are now handled by AIService.generate_report() which includes all this functionality
    
    def find_replace(self):
        """Find and replace values - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, count, status_msg, details):
            """Callback when find/replace complete"""
            self.df = cleaned_df
            self.update_autosave_data()
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_find_replace_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def standardize_text_case(self):
        """Standardize text case - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, col, case, status_msg):
            """Callback when case standardization complete"""
            self.df = cleaned_df
            self.update_autosave_data()
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_standardize_text_case_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def remove_empty(self):
        """Remove empty rows/columns - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, rows_removed, cols_removed, status_msg):
            """Callback when empty rows/columns removed"""
            self.df = cleaned_df
            self.update_autosave_data()
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_remove_empty_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def trim_all_columns(self):
        """Trim whitespace from all text columns - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, count, status_msg):
            """Callback when trim complete"""
            self.df = cleaned_df
            self.update_autosave_data()
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.confirm_trim_all_columns(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def convert_data_types(self):
        """Convert data types - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, col, target_type, status_msg):
            """Callback when conversion complete"""
            self.df = cleaned_df
            self.update_autosave_data()
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_convert_data_types_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def standardize_dates(self):
        """Standardize date formats - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, col, fmt, status_msg):
            """Callback when date standardization complete"""
            self.df = cleaned_df
            self.update_autosave_data()
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_standardize_dates_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def remove_special_chars(self):
        """Remove special characters - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        def on_complete(cleaned_df, col, status_msg):
            """Callback when special characters removed"""
            self.df = cleaned_df
            self.update_autosave_data()
            self.update_info_panel()
            self.view_data()
            self.update_status(status_msg)
        
        # Use dialog factory
        CleaningDialogs.show_remove_special_chars_dialog(
            self.root, self.df, self.cleaning_service, on_complete
        )
    
    def split_merge_columns(self):
        """Split or merge columns - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Chooser dialog
        choice_dialog = tk.Toplevel(self.root)
        choice_dialog.title("Split/Merge Columns")
        choice_dialog.geometry("400x250")
        ttk.Label(choice_dialog, text="Split or Merge Columns", font=('Arial', 12, 'bold')).pack(pady=20)
        ttk.Label(choice_dialog, text="What would you like to do?", font=('Arial', 10)).pack(pady=10)
        
        def open_split():
            choice_dialog.destroy()
            
            def on_complete(cleaned_df, col, num_cols, status_msg):
                """Callback when split complete"""
                self.df = cleaned_df
                self.update_autosave_data()
                self.update_info_panel()
                self.view_data()
                self.update_status(status_msg)
            
            CleaningDialogs.show_split_column_dialog(
                self.root, self.df, self.cleaning_service, on_complete
            )
        
        def open_merge():
            choice_dialog.destroy()
            
            def on_complete(cleaned_df, col1, col2, new_name, status_msg):
                """Callback when merge complete"""
                self.df = cleaned_df
                self.update_autosave_data()
                self.update_info_panel()
                self.view_data()
                self.update_status(status_msg)
            
            CleaningDialogs.show_merge_columns_dialog(
                self.root, self.df, self.cleaning_service, on_complete
            )
        
        btn_frame = ttk.Frame(choice_dialog)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Split Column", command=open_split, 
                  style='Action.TButton', width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Merge Columns", command=open_merge, 
                  style='Action.TButton', width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Cancel", command=choice_dialog.destroy, width=15).pack(pady=5)
    
    def plot_histogram(self):
        """Create histogram - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        VisualizationDialogs.show_histogram_dialog(self.root, self.df, self.create_plot)
    
    def plot_boxplot(self):
        """Create box plot - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        VisualizationDialogs.show_boxplot_dialog(self.root, self.df, self.create_plot)
    
    def plot_scatter(self):
        """Create scatter plot - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        VisualizationDialogs.show_scatter_plot_dialog(self.root, self.df, self.create_plot)
    
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
        """Create pie chart - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        VisualizationDialogs.show_pie_chart_dialog(self.root, self.df, self.create_plot)
    
    def plot_bar(self):
        """Create bar chart - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        VisualizationDialogs.show_bar_chart_dialog(self.root, self.df, self.create_plot)
    
    def plot_line(self):
        """Create line chart - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        VisualizationDialogs.show_line_chart_dialog(self.root, self.df, self.create_plot)
    
    def plot_distribution(self):
        """Create distribution plot - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        VisualizationDialogs.show_distribution_plot_dialog(self.root, self.df, self.create_plot)
    
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
        """Analyze time series data - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        AnalysisDialogs.show_time_series_dialog(self.root, self.df, self.create_plot)
    
    def ecommerce_dashboard(self):
        """Create e-commerce analytics dashboard"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "🛍️  E-COMMERCE ANALYTICS DASHBOARD\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        self.output_text.update_idletasks()  # Show header
        
        # Key metrics
        self.output_text.insert(tk.END, "📊 KEY METRICS:\n")
        self.output_text.insert(tk.END, "-" * 80 + "\n")
        self.output_text.insert(tk.END, f"Total Records: {len(self.df):,}\n")
        self.output_text.insert(tk.END, f"Date Range: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        self.output_text.update_idletasks()  # Show key metrics
        
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
            self.output_text.update_idletasks()  # Show revenue analysis
        
        # Customer analysis
        customer_cols = [col for col in self.df.columns if 'customer' in col.lower() or 'user' in col.lower()]
        if customer_cols:
            self.output_text.insert(tk.END, f"👥 CUSTOMER INSIGHTS:\n")
            for col in customer_cols[:2]:
                unique_count = self.df[col].nunique()
                self.output_text.insert(tk.END, f"  Unique {col}: {unique_count:,}\n")
            self.output_text.update_idletasks()  # Show customer insights
        
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n")
        self.output_text.insert(tk.END, "💡 Use Visualize menu for detailed charts\n")
        self.output_text.update_idletasks()  # Show complete
        
        self.notebook.select(0)
        self.update_status("Dashboard generated")
    
    def column_analysis(self):
        """Detailed analysis of a specific column - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Create callbacks
        def output_callback(text):
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, text)
            self.output_text.update_idletasks()
        
        def notebook_callback():
            self.notebook.select(0)
        
        # Use dialog factory
        AnalysisDialogs.show_column_analysis_dialog(
            self.root, self.df, output_callback, 
            notebook_callback, self.update_status
        )
    
    def filter_data(self):
        """Filter data interactively"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        messagebox.showinfo("Coming Soon", "Interactive filtering will be added in next version!")
    
    def sort_data(self):
        """Sort data by column(s) - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Create callbacks
        def output_callback(text):
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, text)
            self.output_text.update_idletasks()
        
        def notebook_callback():
            self.notebook.select(0)
        
        # Use dialog factory
        sorted_df = AnalysisDialogs.show_sort_data_dialog(
            self.root, self.df, self.analysis_service,
            output_callback, notebook_callback,
            self.update_info_panel, self.update_status
        )
        
        if sorted_df is not None:
            self.df = sorted_df
    
    def convert_dtypes(self):
        """Convert column data types - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Create callbacks
        def output_callback(text):
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, text)
            self.output_text.update_idletasks()
        
        def notebook_callback():
            self.notebook.select(0)
        
        # Use dialog factory
        result_df = CleaningDialogs.show_convert_dtypes_dialog(
            self.root, self.df, output_callback, notebook_callback,
            self.update_info_panel, self.update_status
        )
        
        if result_df is not None:
            self.df = result_df
    
    def groupby_analysis(self):
        """Group by analysis - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Create callbacks
        def output_callback(text):
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, text)
            self.output_text.update_idletasks()
        
        def notebook_callback():
            self.notebook.select(0)
        
        # Use dialog factory
        AnalysisDialogs.show_groupby_dialog(
            self.root, self.df, output_callback, 
            self.display_results_in_grid, notebook_callback, 
            self.update_status
        )
    
    def pivot_table_analysis(self):
        """Pivot table - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        AnalysisDialogs.show_pivot_table_dialog(self.root)
    
    def correlation_analysis(self):
        """Correlation analysis - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Create output callback
        def display_output(text):
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, text)
            self.output_text.update_idletasks()
            self.notebook.select(0)
            self.update_status("Correlation analysis completed")
        
        # Use dialog factory
        AnalysisDialogs.show_correlation_analysis(self.df, display_output)
    
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
        """Execute SQL query - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        AnalysisDialogs.show_sql_query_dialog(self.root, self.df, self.update_status)
    
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
        self.output_text.update_idletasks()  # Show header immediately
        
        profile = DataProfiler.generate_profile(self.df)
        
        # Overview
        self.output_text.insert(tk.END, "DATASET OVERVIEW:\n")
        self.output_text.insert(tk.END, "-" * 80 + "\n")
        for key, value in profile['overview'].items():
            self.output_text.insert(tk.END, f"  {key}: {value}\n")
        self.output_text.update_idletasks()  # Show overview
        
        # Quality Score
        self.output_text.insert(tk.END, f"\n📊 DATA QUALITY SCORE: {profile['quality']['quality_score']}/100\n\n")
        self.output_text.update_idletasks()  # Show quality score
        
        # Issues
        if profile['quality']['total_issues'] > 0:
            self.output_text.insert(tk.END, f"⚠️ ISSUES FOUND ({profile['quality']['total_issues']}):\n")
            for issue in profile['quality']['issues'][:10]:
                self.output_text.insert(tk.END, f"  [{issue['severity']}] {issue['type']}: {issue['column']}\n")
            self.output_text.update_idletasks()  # Show issues
        
        # Recommendations
        self.output_text.insert(tk.END, f"\n💡 RECOMMENDATIONS ({len(profile['recommendations'])}):\n")
        for rec in profile['recommendations']:
            self.output_text.insert(tk.END, f"  [{rec['priority']}] {rec['action']}: {rec['reason']}\n")
        self.output_text.update_idletasks()  # Show recommendations
        
        # Strong correlations
        if profile['correlations'].get('strong_correlations'):
            self.output_text.insert(tk.END, f"\n🔗 STRONG CORRELATIONS:\n")
            for corr in profile['correlations']['strong_correlations'][:5]:
                self.output_text.insert(tk.END, f"  {corr['col1']} ↔ {corr['col2']}: {corr['correlation']:.3f} ({corr['strength']})\n")
            self.output_text.update_idletasks()  # Show correlations
        
        self.notebook.select(0)
        self.update_status("Data profiling report generated")
        messagebox.showinfo("Success", "Data profiling report generated!")
    
    def statistical_tests(self):
        """Perform statistical tests - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        AnalysisDialogs.show_statistical_tests_dialog(self.root, self.df)
    
    def ab_testing(self):
        """A/B Testing - delegates to dialog"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Use dialog factory
        AnalysisDialogs.show_ab_testing_dialog(self.root, self.df)
    
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
        self.output_text.update_idletasks()  # Show immediately
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
        self.output_text.update_idletasks()  # Show immediately
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

FILE OPERATIONS:
Ctrl+O - Import CSV file
Ctrl+E - Export CSV file  
Ctrl+Q - Quit application

DATA OPERATIONS:
Ctrl+D - View Data
Ctrl+S - Show Statistics
Ctrl+R - Reset Data to original
Ctrl+F - Advanced Filters

HELP:
F1 - About NexData

TIP: All shortcuts work with capital or lowercase!
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def change_theme(self, theme_name):
        """Change application theme"""
        self.theme_manager.apply_theme(theme_name)
        theme_display = self.theme_manager.get_theme_display_name(theme_name)
        self.update_status(f"Theme changed to: {theme_display}")
        messagebox.showinfo("Theme Changed", f"Theme set to: {theme_display}\n\nSome elements may require restart for full effect.")
    
    # === NEW ADVANCED FEATURES ===
    
    def pivot_table(self):
        """Create pivot table guide"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Create a helpful window with examples
        pivot_window = tk.Toplevel(self.root)
        pivot_window.title("Pivot Table - How to Use")
        pivot_window.geometry("750x650")
        
        content = """PIVOT TABLES in NexData

🎯 WHAT IS A PIVOT TABLE?
A pivot table summarizes data by grouping and aggregating.

Example: Summarize employee salaries by department

ORIGINAL DATA:
Name          | Department   | Salary
John Doe      | Sales        | 55000
Jane Smith    | Engineering  | 75000
Bob Johnson   | Sales        | 65000

PIVOT TABLE RESULT:
Department   | Average Salary | Count
Sales        | 60,000         | 2
Engineering  | 75,000         | 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 HOW TO CREATE IN NEXDATA:

Use Analysis > SQL Query (MORE POWERFUL than traditional pivot tables!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 EXAMPLE QUERIES FOR YOUR DATA:

1. BASIC PIVOT - Average by Group:
SELECT Department, 
       AVG(Salary) as Avg_Salary,
       COUNT(*) as Count
FROM data
GROUP BY Department

2. SUM BY CATEGORY:
SELECT Department, 
       SUM(Salary) as Total_Salary
FROM data
GROUP BY Department

3. MULTIPLE AGGREGATIONS:
SELECT Department,
       AVG(Salary) as Avg_Salary,
       MIN(Salary) as Min_Salary,
       MAX(Salary) as Max_Salary,
       COUNT(*) as Employees
FROM data
GROUP BY Department
ORDER BY Avg_Salary DESC

4. PIVOT WITH FILTERING:
SELECT Department,
       AVG(Salary) as Avg_Salary
FROM data
WHERE Experience > 5
GROUP BY Department

5. TRUE PIVOT (Columns from Rows):
SELECT 
    CASE WHEN Experience < 3 THEN 'Junior'
         WHEN Experience < 8 THEN 'Mid'
         ELSE 'Senior' END as Level,
    AVG(CASE WHEN Department='Sales' THEN Salary END) as Sales,
    AVG(CASE WHEN Department='Engineering' THEN Salary END) as Engineering,
    AVG(CASE WHEN Department='Marketing' THEN Salary END) as Marketing
FROM data
GROUP BY Level

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ TO EXPORT RESULTS:
1. Run SQL Query
2. Results appear in Output tab
3. Copy (Ctrl+A then Ctrl+C)
4. Paste into Excel or Google Sheets

OR generate HTML report: File > Generate Executive Report

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS:
• Replace "Department" with your column name
• Replace "Salary" with the column you want to aggregate
• Table name is always "data" (lowercase)
• Check Dataset Info panel for exact column names
• Start simple, then add complexity

🆘 MORE HELP:
• Help > User Guide & Tutorials
• docs/PIVOT_SQL_GUIDE.md (detailed guide)
"""
        
        # Add scrolled text widget
        text_widget = scrolledtext.ScrolledText(pivot_window, wrap=tk.WORD, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        text_widget.insert(1.0, content)
        text_widget.config(state='disabled')  # Read-only
        
        # Add buttons
        btn_frame = ttk.Frame(pivot_window)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Open SQL Query", command=lambda: [pivot_window.destroy(), self.sql_query()], width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View Full Guide", command=self.show_pivot_guide, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=pivot_window.destroy, width=12).pack(side=tk.LEFT, padx=5)
        
        self.update_status("Pivot table guide opened")
    
    def show_pivot_guide(self):
        """Show comprehensive pivot/SQL guide"""
        try:
            guide_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'docs', 'PIVOT_SQL_GUIDE.md')
            if os.path.exists(guide_path):
                with open(guide_path, 'r', encoding='utf-8') as f:
                    guide_content = f.read()
                
                guide_window = tk.Toplevel(self.root)
                guide_window.title("Pivot Tables & SQL Query - Complete Guide")
                guide_window.geometry("950x750")
                
                text_widget = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, font=('Courier', 10))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(1.0, guide_content)
                text_widget.config(state='disabled')
                
                ttk.Button(guide_window, text="Close", command=guide_window.destroy).pack(pady=5)
                self.update_status("Pivot/SQL guide opened")
            else:
                messagebox.showinfo("Guide", "Guide file not found.\n\nUse Analysis > SQL Query to create pivot tables.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open guide:\n{str(e)}")
    
    def advanced_filters(self):
        """Apply advanced filters with GUI"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Advanced Filters")
        dialog.geometry("700x550")
        
        ttk.Label(dialog, text="Advanced Filters - Build Complex Queries", 
                 font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Instructions
        info_frame = ttk.LabelFrame(dialog, text="How to Use", padding=10)
        info_frame.pack(pady=10, padx=20, fill=tk.X)
        ttk.Label(info_frame, text="• Add multiple filter conditions\n"
                                   "• Combine with AND/OR logic\n"
                                   "• Preview results before applying",
                 justify=tk.LEFT).pack()
        
        # Filter conditions container
        conditions_frame = ttk.LabelFrame(dialog, text="Filter Conditions", padding=10)
        conditions_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Scrollable frame for conditions
        canvas = tk.Canvas(conditions_frame, height=200)
        scrollbar = ttk.Scrollbar(conditions_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store filter conditions
        filter_conditions = []
        
        def add_condition():
            """Add a new filter condition row"""
            condition_frame = ttk.Frame(scrollable_frame)
            condition_frame.pack(fill=tk.X, pady=5)
            
            # Condition number
            row_num = len(filter_conditions) + 1
            ttk.Label(condition_frame, text=f"{row_num}.", width=3).pack(side=tk.LEFT, padx=5)
            
            # Logic operator (AND/OR) - skip for first condition
            logic_var = tk.StringVar(value="AND")
            if row_num > 1:
                logic_combo = ttk.Combobox(condition_frame, textvariable=logic_var, 
                                          values=["AND", "OR"], state='readonly', width=6)
                logic_combo.pack(side=tk.LEFT, padx=5)
            else:
                ttk.Label(condition_frame, text="      ", width=6).pack(side=tk.LEFT, padx=5)
            
            # Column selection
            column_var = tk.StringVar()
            column_combo = ttk.Combobox(condition_frame, textvariable=column_var,
                                       values=list(self.df.columns), state='readonly', width=15)
            column_combo.pack(side=tk.LEFT, padx=5)
            if len(self.df.columns) > 0:
                column_combo.current(0)
            
            # Operator selection
            operator_var = tk.StringVar(value="==")
            operator_combo = ttk.Combobox(condition_frame, textvariable=operator_var,
                                         values=["==", "!=", ">", "<", ">=", "<=", "contains", "not contains"],
                                         state='readonly', width=12)
            operator_combo.pack(side=tk.LEFT, padx=5)
            
            # Value input
            value_var = tk.StringVar()
            value_entry = ttk.Entry(condition_frame, textvariable=value_var, width=15)
            value_entry.pack(side=tk.LEFT, padx=5)
            
            # Remove button
            def remove_this():
                condition_frame.destroy()
                filter_conditions.remove(condition_data)
                # Update row numbers
                for idx, cond in enumerate(filter_conditions, 1):
                    cond['label'].config(text=f"{idx}.")
            
            remove_btn = ttk.Button(condition_frame, text="×", width=3, command=remove_this)
            remove_btn.pack(side=tk.LEFT, padx=5)
            
            # Store condition data
            condition_data = {
                'frame': condition_frame,
                'label': condition_frame.winfo_children()[0],
                'logic': logic_var,
                'column': column_var,
                'operator': operator_var,
                'value': value_var
            }
            filter_conditions.append(condition_data)
        
        # Add condition button
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="+ Add Condition", command=add_condition).pack(side=tk.LEFT, padx=5)
        
        # Preview area
        preview_frame = ttk.LabelFrame(dialog, text="Preview (First 10 rows)", padding=10)
        preview_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        preview_text = tk.Text(preview_frame, height=8, width=70, wrap=tk.NONE)
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
        preview_text.config(yscrollcommand=preview_scroll.set)
        preview_text.grid(row=0, column=0, sticky='nsew')
        preview_scroll.grid(row=0, column=1, sticky='ns')
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_text.config(state=tk.DISABLED)
        
        def build_filter_query():
            """Build pandas query from conditions"""
            if not filter_conditions:
                return None
            
            query_parts = []
            for idx, cond in enumerate(filter_conditions):
                col = cond['column'].get()
                op = cond['operator'].get()
                val = cond['value'].get()
                
                if not col or not val:
                    continue
                
                # Handle different operators
                if op == "contains":
                    query_part = f"`{col}`.astype(str).str.contains('{val}', case=False, na=False)"
                elif op == "not contains":
                    query_part = f"~`{col}`.astype(str).str.contains('{val}', case=False, na=False)"
                else:
                    # Try to convert value to appropriate type
                    try:
                        if self.df[col].dtype in ['int64', 'float64']:
                            val_formatted = float(val)
                        else:
                            val_formatted = f"'{val}'"
                        query_part = f"`{col}` {op} {val_formatted}"
                    except:
                        query_part = f"`{col}`.astype(str) {op} '{val}'"
                
                if idx > 0:
                    logic = cond['logic'].get()
                    query_parts.append(f" {logic.lower()} {query_part}")
                else:
                    query_parts.append(query_part)
            
            return "".join(query_parts) if query_parts else None
        
        def preview_filter():
            """Preview filter results"""
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            try:
                query = build_filter_query()
                if not query:
                    preview_text.insert(tk.END, "⚠️ Please add at least one filter condition\n")
                    preview_text.config(state=tk.DISABLED)
                    return
                
                # Apply filter
                filtered_df = self.df.query(query)
                
                if len(filtered_df) == 0:
                    preview_text.insert(tk.END, "⚠️ No rows match the filter criteria\n\n")
                    preview_text.insert(tk.END, f"Query: {query}")
                else:
                    preview_text.insert(tk.END, f"✓ Found {len(filtered_df)} matching rows (showing first 10):\n\n")
                    preview_text.insert(tk.END, filtered_df.head(10).to_string())
                
            except Exception as e:
                preview_text.insert(tk.END, f"❌ Error: {str(e)}\n\nPlease check your filter conditions.")
            
            preview_text.config(state=tk.DISABLED)
        
        def apply_filter():
            """Apply the filter to the dataframe"""
            try:
                query = build_filter_query()
                if not query:
                    messagebox.showwarning("Warning", "Please add at least one filter condition!")
                    return
                
                before_count = len(self.df)
                # Use pandas query directly (complex multi-condition filtering)
                # AnalysisService.filter_data() is for single conditions
                self.df = self.df.query(query)
                after_count = len(self.df)
                
                # Output results
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "ADVANCED FILTER APPLIED\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n\n")
                self.output_text.insert(tk.END, f"Filter Query: {query}\n\n")
                self.output_text.insert(tk.END, f"✓ Original rows: {before_count}\n")
                self.output_text.insert(tk.END, f"✓ Filtered rows: {after_count}\n")
                self.output_text.insert(tk.END, f"✓ Rows removed: {before_count - after_count}\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.update_idletasks()
                self.notebook.select(0)
                
                self.update_info_panel()
                self.view_data()
                self.update_status(f"Filter applied: {after_count} rows")
                
                messagebox.showinfo("Success", 
                                  f"Filter applied successfully!\n\n"
                                  f"Original rows: {before_count}\n"
                                  f"Filtered rows: {after_count}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply filter:\n{str(e)}")
        
        # Action buttons
        action_frame = ttk.Frame(dialog)
        action_frame.pack(pady=15)
        
        ttk.Button(action_frame, text="Preview", command=preview_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Apply Filter", command=apply_filter, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Add first condition by default
        add_condition()
    
    def data_quality_check(self):
        """Run data quality assessment"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        from data_ops.data_quality import DataQualityChecker
        self.perf_monitor.start_operation('data_quality_check')
        quality_report = DataQualityChecker.assess_quality(self.df)
        report_text = DataQualityChecker.generate_quality_report_text(quality_report)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, report_text)
        self.notebook.select(0)
        self.perf_monitor.end_operation('data_quality_check')
        self.update_status(f"Data quality: {quality_report['quality_level']} ({quality_report['overall_score']:.0f}/100)")
    
    def auto_insights(self):
        """Generate automated insights"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        from analysis.auto_insights import AutoInsights
        insights = AutoInsights.generate_insights(self.df)
        output = f"\n{'='*60}\nAUTO-GENERATED INSIGHTS\n{'='*60}\n\n"
        output += "SUMMARY:\n"
        for item in insights['summary']:
            output += f"• {item}\n"
        if insights['trends']:
            output += "\nTRENDS:\n"
            for item in insights['trends']:
                output += f"• {item}\n"
        if insights['correlations']:
            output += "\nCORRELATIONS:\n"
            for item in insights['correlations']:
                output += f"• {item}\n"
        if insights['recommendations']:
            output += "\nRECOMMENDATIONS:\n"
            for item in insights['recommendations']:
                output += f"✓ {item}\n"
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output)
        self.output_text.update_idletasks()  # Show immediately
        self.notebook.select(0)
        self.update_status("Auto insights generated")
    
    def rfm_segmentation(self):
        """RFM Customer Segmentation"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        messagebox.showinfo("RFM Segmentation", "RFM (Recency, Frequency, Monetary) analysis requires:\n\n• Customer ID column\n• Transaction date column\n• Revenue column\n\nUse Analysis > E-commerce Dashboard for customer insights.")
    
    def time_series_forecasting(self):
        """Time series forecasting"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        messagebox.showinfo("Forecasting", "Time series forecasting module available.\n\nUse Analysis > Time Series Analysis for trend analysis and predictions.")
    
    def sales_dashboard(self):
        """Sales analytics dashboard"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        messagebox.showinfo("Sales Dashboard", "Sales dashboard requires:\n• Date column\n• Revenue column\n• (Optional) Product column\n• (Optional) Customer column\n\nUse Analysis > E-commerce Dashboard.")
    
    def customer_dashboard(self):
        """Customer analytics dashboard"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        messagebox.showinfo("Customer Dashboard", "Customer analytics available through:\n\nAnalysis > E-commerce Dashboard\n\nProvides customer insights, retention, and segmentation.")
    
    def compare_datasets(self):
        """Compare two datasets"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        from data_ops.data_comparison import DataComparison
        file_path = filedialog.askopenfilename(title="Select second dataset", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            df2 = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
            comparison = DataComparison.compare_dataframes(self.df, df2)
            output = f"=== DATASET COMPARISON ===\n\nDataset 1: {comparison['df1_shape']}\nDataset 2: {comparison['df2_shape']}\n\nCommon Columns: {len(comparison['common_columns'])}\n"
            if comparison['only_in_df1']:
                output += f"Only in DF1: {', '.join(comparison['only_in_df1'])}\n"
            if comparison['only_in_df2']:
                output += f"Only in DF2: {', '.join(comparison['only_in_df2'])}\n"
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, output)
            self.output_text.update_idletasks()  # Show immediately
            self.notebook.select(0)
            self.update_status("Comparison complete")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare:\n{str(e)}")
    
    def export_powerpoint(self):
        """Export to PowerPoint"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        from data_ops.pptx_export import PowerPointExporter
        available, msg = PowerPointExporter.check_pptx_available()
        if not available:
            messagebox.showwarning("Package Required", "Install python-pptx:\npip install python-pptx")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pptx", filetypes=[("PowerPoint", "*.pptx")])
        if file_path:
            success, msg = PowerPointExporter.create_presentation(self.df, file_path)
            if success:
                messagebox.showinfo("Success", msg)
                self.update_status("Exported to PowerPoint")
            else:
                messagebox.showerror("Error", msg)
    
    def performance_monitor(self):
        """Show performance monitoring report"""
        report = self.perf_monitor.get_performance_report()
        report_text = self.perf_monitor.format_performance_report(report)
        tips = self.perf_monitor.get_optimization_tips(report)
        report_text += "\n=== OPTIMIZATION TIPS ===\n"
        for tip in tips:
            report_text += f"{tip}\n"
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, report_text)
        self.output_text.update_idletasks()  # Show immediately
        self.notebook.select(0)
        self.update_status("Performance report generated")
    
    def show_user_guide(self):
        """Display comprehensive user guide"""
        try:
            guide_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'docs', 'USER_GUIDE.md')
            if os.path.exists(guide_path):
                with open(guide_path, 'r', encoding='utf-8') as f:
                    guide_content = f.read()
                
                # Create a new window for the guide
                guide_window = tk.Toplevel(self.root)
                guide_window.title("NexData - User Guide & Tutorials")
                guide_window.geometry("900x700")
                
                # Add scrolled text widget
                text_widget = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, font=('Courier', 10))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(1.0, guide_content)
                text_widget.config(state='disabled')  # Read-only
                
                # Add close button
                ttk.Button(guide_window, text="Close", command=guide_window.destroy).pack(pady=5)
                
                self.update_status("User guide opened")
            else:
                messagebox.showinfo("User Guide", "User guide file not found.\n\nAccess online: https://github.com/YEXIU21/NexData")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open user guide:\n{str(e)}")
    
    def show_quick_start(self):
        """Show quick start guide"""
        quick_start = """NEXDATA - QUICK START GUIDE
        
🚀 GET STARTED IN 5 MINUTES!

STEP 1: IMPORT YOUR DATA
• File > Import CSV (or Import Excel)
• Select your data file
• ✅ Data loads automatically

STEP 2: VIEW YOUR DATA
• Click "View Data" button (left panel)
• Browse your dataset
• Check columns and data types

STEP 3: CHECK DATA QUALITY
• Data > Data Quality Check
• Review quality score (0-100)
• Follow recommendations

STEP 4: RUN AUTO INSIGHTS
• Analysis > Auto Insights
• Get automated pattern detection
• Review trends and correlations

STEP 5: CREATE VISUALIZATIONS
• Visualize > Histogram (or any chart type)
• Select column to visualize
• Use zoom/pan tools to explore

STEP 6: EXPORT RESULTS
• File > Generate Executive Report
• Professional HTML report created
• Opens in browser automatically

📊 COMMON TASKS:

SQL QUERIES (Most Powerful!):
• Analysis > SQL Query
• Example: SELECT * FROM data WHERE Salary > 50000
• Example: SELECT Department, AVG(Salary) FROM data GROUP BY Department

CUSTOMER ANALYSIS:
• Analysis > RFM Customer Segmentation
• Identifies Champions, Loyal, At-Risk customers
• Perfect for marketing campaigns

SALES FORECASTING:
• Analysis > Time Series Forecasting
• Predict future sales/revenue
• Choose: Linear Trend, Moving Average, or Exponential Smoothing

DATA COMPARISON:
• Tools > Compare Datasets
• Load second file to compare
• See differences automatically

💡 TIPS:
• Always check Data Quality first
• Use Auto Insights for quick overview
• SQL Query can do almost anything
• Export reports for presentations
• Try different themes (View > Theme)

🆘 NEED HELP?
• Help > User Guide & Tutorials (full documentation)
• Help > Performance Monitor (if slow)
• Help > About (feature list)

🎯 RECOMMENDED WORKFLOW:
1. Import data
2. Data Quality Check
3. Clean data (remove duplicates/outliers)
4. Auto Insights
5. Detailed analysis (SQL/Statistics)
6. Visualizations
7. Generate reports

✨ YOU'RE READY! Start exploring your data!

For detailed tutorials: Help > User Guide & Tutorials
"""
        
        # Create scrollable window instead of messagebox
        quick_window = tk.Toplevel(self.root)
        quick_window.title("NexData - Quick Start Guide")
        quick_window.geometry("700x600")
        
        # Add scrolled text widget
        text_widget = scrolledtext.ScrolledText(quick_window, wrap=tk.WORD, font=('Arial', 11))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        text_widget.insert(1.0, quick_start)
        text_widget.config(state='disabled')  # Read-only
        
        # Add close button
        btn_frame = ttk.Frame(quick_window)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Close", command=quick_window.destroy, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Open Full Guide", command=self.show_user_guide, width=15).pack(side=tk.LEFT, padx=5)
        
        self.update_status("Quick Start Guide opened")
    
    def show_about(self):
        about_text = """NexData v3.0 - Professional Data Analysis
Shopify Edition - Next-Generation Analytics

Created for E-commerce & Shopify Data Analysts

✨ 60+ Features Including:
• Data Import/Export (CSV, Excel, JSON, PowerPoint)
• Advanced Data Cleaning & Quality Assessment
• Statistical Analysis & A/B Testing
• RFM Customer Segmentation (10 segments)
• Time Series Forecasting (3 methods)
• Auto Insights & Anomaly Detection
• Sales/Customer Dashboards
• SQL Query Interface
• 10+ Visualization Types
• Data Comparison Tool
• Theme Support (System/Light/Dark)
• Performance Monitoring

🎯 Perfect for analyzing:
- Sales trends & Revenue forecasting
- Customer segmentation & Retention
- Product performance & Inventory
- Marketing campaign effectiveness
- Data quality & Validation

🚀 NEW in v3.0:
• Pivot Tables • RFM Analysis • Auto Insights
• Forecasting • Quality Checker • Dashboards
• Dataset Comparison • PowerPoint Export

👨‍💻 Developed by: YEXIU21

© 2025 NexData - Built with Python, Pandas, Matplotlib
Next-Generation Data Analytics Platform"""
        
        messagebox.showinfo("About NexData v3.0", about_text)


# Entry point moved to src/main.py following SEPARATION OF CONCERNS principle
