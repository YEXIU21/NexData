"""
Tooltip System - Modern hover tooltips for better UX
Shows helpful hints when user hovers over UI elements
"""

import tkinter as tk
from tkinter import ttk


class ToolTip:
    """
    Create a tooltip for a given widget with modern styling
    """
    
    def __init__(self, widget, text='', delay=500, wrap_length=200):
        """
        Initialize tooltip
        
        Parameters:
        -----------
        widget : tk.Widget
            Widget to attach tooltip to
        text : str
            Tooltip text
        delay : int
            Delay in milliseconds before showing tooltip
        wrap_length : int
            Maximum width for text wrapping
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wrap_length = wrap_length
        self.tooltip_window = None
        self.after_id = None
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
    
    def on_enter(self, event=None):
        """Handle mouse enter event"""
        self.schedule_tooltip()
    
    def on_leave(self, event=None):
        """Handle mouse leave event"""
        self.cancel_tooltip()
        self.hide_tooltip()
    
    def schedule_tooltip(self):
        """Schedule tooltip to show after delay"""
        self.cancel_tooltip()
        self.after_id = self.widget.after(self.delay, self.show_tooltip)
    
    def cancel_tooltip(self):
        """Cancel scheduled tooltip"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
    
    def show_tooltip(self):
        """Show tooltip window"""
        if self.tooltip_window or not self.text:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Styling
        frame = tk.Frame(self.tooltip_window, 
                        background="#ffffe0",
                        borderwidth=1,
                        relief="solid")
        frame.pack()
        
        label = tk.Label(frame,
                        text=self.text,
                        justify=tk.LEFT,
                        background="#ffffe0",
                        foreground="#000000",
                        relief=tk.FLAT,
                        borderwidth=0,
                        wraplength=self.wrap_length,
                        font=('TkDefaultFont', 9))
        label.pack(padx=6, pady=4)
    
    def hide_tooltip(self):
        """Hide tooltip window"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def create_tooltip(widget, text, delay=500):
    """
    Convenience function to create tooltip
    
    Parameters:
    -----------
    widget : tk.Widget
        Widget to attach tooltip to
    text : str
        Tooltip text
    delay : int
        Delay in milliseconds
    
    Returns:
    --------
    ToolTip
        Tooltip instance
    
    Example:
    --------
    button = ttk.Button(root, text="Click me")
    create_tooltip(button, "This button does something cool!")
    """
    return ToolTip(widget, text, delay)


def add_tooltips_to_menu(menu, tooltips_dict):
    """
    Add tooltips to menu items (shows in status bar instead)
    
    Parameters:
    -----------
    menu : tk.Menu
        Menu to add tooltips to
    tooltips_dict : dict
        Dictionary mapping item labels to tooltip text
    """
    # Note: Menu items can't have hover tooltips in Tkinter
    # This is a placeholder for future enhancement
    # Could show tooltip in status bar when menu item is highlighted
    pass


# Common tooltip messages for NexData
COMMON_TOOLTIPS = {
    'import_csv': 'Import data from CSV file (Ctrl+O)\nSupports large files with progress tracking',
    'import_excel': 'Import data from Excel file\nSupports .xlsx and .xls formats',
    'export_csv': 'Export current data to CSV format (Ctrl+E)',
    'export_excel': 'Export current data to Excel format',
    'view_data': 'Display first 100 rows of data (Ctrl+D)',
    'statistics': 'Show descriptive statistics (Ctrl+S)\nMean, median, std dev, quartiles',
    'reset_data': 'Reset to original imported data (Ctrl+R)\nClears all filters and modifications',
    'advanced_filters': 'Create complex data filters (Ctrl+F)\nCombine multiple conditions with AND/OR',
    'remove_duplicates': 'Remove duplicate rows from dataset\nSelect columns to check for duplicates',
    'missing_values': 'Handle missing data\nOptions: drop, fill, forward/backward fill',
    'ai_advisor': 'Get AI recommendations for data quality\nAutomatically detects issues',
    'ai_report': 'Generate comprehensive AI analysis report\nIncludes insights, quality score, recommendations',
}
