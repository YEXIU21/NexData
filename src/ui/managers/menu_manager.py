"""
Menu Manager
Handles menu creation and configuration
Extracted from main_window.py
"""

import tkinter as tk
from tkinter import ttk


class MenuManager:
    """Manages application menu bar"""
    
    def __init__(self, root, app):
        """
        Initialize Menu Manager
        
        Args:
            root: Tkinter root window
            app: Reference to main application for callbacks
        """
        self.root = root
        self.app = app
    
    def create_menu(self):
        """Create complete menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import CSV", command=self.app.import_csv, accelerator="Ctrl+O")
        file_menu.add_command(label="Import Excel", command=self.app.import_excel, accelerator="Ctrl+Shift+O")
        file_menu.add_command(label="API Connector", command=self.app.open_api_connector)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV", command=self.app.export_csv, accelerator="Ctrl+S")
        file_menu.add_command(label="Export to Excel", command=self.app.export_excel, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Export to JSON", command=self.app.export_json)
        file_menu.add_command(label="Export Excel with Pivot", command=self.app.export_excel_with_pivot)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="View Data", command=self.app.view_data, accelerator="Ctrl+1")
        view_menu.add_command(label="Data Info", command=self.app.show_data_info, accelerator="Ctrl+2")
        view_menu.add_command(label="Statistics", command=self.app.show_statistics, accelerator="Ctrl+3")
        view_menu.add_separator()
        view_menu.add_command(label="Reset Data", command=self.app.reset_data, accelerator="Ctrl+R")
        
        # Clean Menu
        clean_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Clean", menu=clean_menu)
        clean_menu.add_command(label="Remove Duplicates", command=self.app.remove_duplicates, accelerator="Ctrl+D")
        clean_menu.add_command(label="Handle Missing Values", command=self.app.handle_missing_values, accelerator="Ctrl+M")
        clean_menu.add_command(label="Remove Outliers", command=self.app.remove_outliers)
        clean_menu.add_command(label="Clean Order IDs", command=self.app.clean_order_ids)
        clean_menu.add_separator()
        clean_menu.add_command(label="Smart Fill Missing", command=self.app.smart_fill_missing)
        clean_menu.add_command(label="Find & Replace", command=self.app.find_replace, accelerator="Ctrl+F")
        clean_menu.add_command(label="Standardize Text Case", command=self.app.standardize_text_case)
        clean_menu.add_command(label="Remove Empty Rows/Columns", command=self.app.remove_empty)
        clean_menu.add_command(label="Trim All Columns", command=self.app.trim_all_columns)
        clean_menu.add_separator()
        clean_menu.add_command(label="Convert Data Types", command=self.app.convert_data_types)
        clean_menu.add_command(label="Standardize Dates", command=self.app.standardize_dates)
        clean_menu.add_command(label="Remove Special Characters", command=self.app.remove_special_chars)
        clean_menu.add_separator()
        clean_menu.add_command(label="Split Column", command=self.app.split_column)
        clean_menu.add_command(label="Merge Columns", command=self.app.merge_columns)
        
        # Analyze Menu
        analyze_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analyze", menu=analyze_menu)
        analyze_menu.add_command(label="Column Analysis", command=self.app.column_analysis)
        analyze_menu.add_command(label="Correlation Analysis", command=self.app.correlation_analysis)
        analyze_menu.add_command(label="Statistical Tests", command=self.app.statistical_tests)
        analyze_menu.add_command(label="A/B Testing", command=self.app.ab_testing)
        analyze_menu.add_separator()
        analyze_menu.add_command(label="Group By Analysis", command=self.app.group_by_analysis, accelerator="Ctrl+G")
        analyze_menu.add_command(label="Pivot Table", command=self.app.pivot_table, accelerator="Ctrl+P")
        analyze_menu.add_separator()
        analyze_menu.add_command(label="SQL Query", command=self.app.sql_query, accelerator="Ctrl+Q")
        analyze_menu.add_command(label="Data Profiling", command=self.app.data_profiling)
        analyze_menu.add_command(label="Auto Insights", command=self.app.auto_insights)
        
        # Visualize Menu
        viz_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualize", menu=viz_menu)
        viz_menu.add_command(label="Bar Chart", command=lambda: self.app.create_visualization('bar'))
        viz_menu.add_command(label="Line Chart", command=lambda: self.app.create_visualization('line'))
        viz_menu.add_command(label="Pie Chart", command=lambda: self.app.create_visualization('pie'))
        viz_menu.add_command(label="Scatter Plot", command=lambda: self.app.create_visualization('scatter'))
        viz_menu.add_command(label="Histogram", command=lambda: self.app.create_visualization('histogram'))
        viz_menu.add_command(label="Box Plot", command=lambda: self.app.create_visualization('boxplot'))
        viz_menu.add_separator()
        viz_menu.add_command(label="Heatmap", command=lambda: self.app.create_visualization('heatmap'))
        viz_menu.add_command(label="Distribution Plot", command=lambda: self.app.create_visualization('distribution'))
        
        # E-commerce Menu
        ecom_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="E-commerce", menu=ecom_menu)
        ecom_menu.add_command(label="RFM Analysis", command=self.app.rfm_analysis)
        ecom_menu.add_command(label="Time Series Forecast", command=self.app.time_series_forecast)
        ecom_menu.add_separator()
        ecom_menu.add_command(label="Sales Dashboard", command=self.app.sales_dashboard)
        ecom_menu.add_command(label="Customer Dashboard", command=self.app.customer_dashboard)
        ecom_menu.add_command(label="E-commerce Dashboard", command=self.app.ecommerce_dashboard)
        
        # AI Menu
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="AI", menu=ai_menu)
        ai_menu.add_command(label="AI Data Quality Advisor", command=self.app.ai_data_quality_advisor)
        ai_menu.add_command(label="AI Report Generator", command=self.app.ai_report_generator)
        
        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Theme Settings", command=self.app.open_theme_settings)
        settings_menu.add_command(label="Preferences", command=self.app.open_preferences)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.app.show_user_guide)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.app.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.app.show_about)
