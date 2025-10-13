"""
Professional Data Analysis Tool - Main Entry Point
Shopify Edition v2.0

This is the main entry point that initializes and runs the application.
Following SEPARATION OF CONCERNS principle - main.py only handles application startup.

© 2025
"""

import tkinter as tk
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.main_window import DataAnalystApp


def main():
    """
    Main function to initialize and run the Data Analyst Tool.
    
    Creates the root Tkinter window and initializes the main application.
    Enters the Tkinter event loop.
    """
    try:
        # Create root window
        root = tk.Tk()
        
        # Initialize application
        app = DataAnalystApp(root)
        
        # Start event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
