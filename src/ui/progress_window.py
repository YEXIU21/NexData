"""
Progress Window - Enterprise-grade progress tracking
Shows detailed progress for long-running operations
"""

import tkinter as tk
from tkinter import ttk
import threading
import time


class ProgressWindow:
    """
    Modern progress window with detailed status
    """
    
    def __init__(self, parent, title="Processing", cancelable=False):
        """
        Initialize progress window
        
        Parameters:
        -----------
        parent : tk.Tk
            Parent window
        title : str
            Window title
        cancelable : bool
            Allow user to cancel operation
        """
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x200")
        self.window.resizable(False, False)
        
        # Center window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.canceled = False
        self.cancelable = cancelable
        
        self._create_ui()
    
    def _create_ui(self):
        """Create UI elements"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        self.title_label = ttk.Label(main_frame, text="Processing...", 
                                     font=('TkDefaultFont', 12, 'bold'))
        self.title_label.pack(pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Starting...", 
                                      font=('TkDefaultFont', 10))
        self.status_label.pack(pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                           maximum=100, length=400, mode='determinate')
        self.progress_bar.pack(pady=10)
        
        # Detail label (small text for technical details)
        self.detail_label = ttk.Label(main_frame, text="", 
                                      font=('TkDefaultFont', 8), foreground='gray')
        self.detail_label.pack(pady=5)
        
        # Cancel button (if cancelable)
        if self.cancelable:
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=10)
            
            self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                           command=self._on_cancel)
            self.cancel_button.pack()
    
    def update(self, progress=None, status=None, detail=None):
        """
        Update progress window
        
        Parameters:
        -----------
        progress : float
            Progress percentage (0-100)
        status : str
            Status message
        detail : str
            Technical detail message
        """
        if progress is not None:
            self.progress_var.set(progress)
        
        if status is not None:
            self.status_label.config(text=status)
        
        if detail is not None:
            self.detail_label.config(text=detail)
        
        self.window.update()
    
    def set_indeterminate(self):
        """Set progress bar to indeterminate mode (continuous animation)"""
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start(10)
    
    def set_determinate(self):
        """Set progress bar to determinate mode (percentage-based)"""
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
    
    def _on_cancel(self):
        """Handle cancel button click"""
        self.canceled = True
        self.status_label.config(text="Canceling...")
        if self.cancelable:
            self.cancel_button.config(state='disabled')
    
    def is_canceled(self):
        """Check if operation was canceled"""
        return self.canceled
    
    def close(self):
        """Close progress window"""
        try:
            self.window.destroy()
        except:
            pass


class BackgroundTask:
    """
    Execute long-running tasks in background with progress tracking
    """
    
    def __init__(self, parent, task_func, title="Processing", cancelable=False):
        """
        Initialize background task
        
        Parameters:
        -----------
        parent : tk.Tk
            Parent window
        task_func : callable
            Function to execute in background
            Must accept progress_callback parameter
        title : str
            Progress window title
        cancelable : bool
            Allow user to cancel
        """
        self.parent = parent
        self.task_func = task_func
        self.title = title
        self.cancelable = cancelable
        
        self.result = None
        self.error = None
        self.progress_window = None
    
    def run(self):
        """
        Run task in background and show progress window
        
        Returns:
        --------
        result : any
            Task result (None if canceled or error)
        """
        # Create progress window
        self.progress_window = ProgressWindow(self.parent, self.title, self.cancelable)
        
        # Start task in background thread
        self.thread = threading.Thread(target=self._execute_task, daemon=True)
        self.thread.start()
        
        # Wait for completion
        while self.thread.is_alive():
            self.parent.update()
            time.sleep(0.1)
        
        # Close progress window
        self.progress_window.close()
        
        # Return result or raise error
        if self.error:
            raise self.error
        
        return self.result
    
    def _execute_task(self):
        """Execute task in background"""
        try:
            # Progress callback
            def progress_callback(progress=None, status=None, detail=None):
                if self.progress_window:
                    self.progress_window.update(progress, status, detail)
                
                # Check if canceled
                if self.cancelable and self.progress_window.is_canceled():
                    raise InterruptedError("Operation canceled by user")
            
            # Execute task
            self.result = self.task_func(progress_callback)
            
        except Exception as e:
            self.error = e


def run_with_progress(parent, task_func, title="Processing", cancelable=False):
    """
    Convenience function to run task with progress window
    
    Parameters:
    -----------
    parent : tk.Tk
        Parent window
    task_func : callable
        Function to execute (must accept progress_callback)
    title : str
        Window title
    cancelable : bool
        Allow cancellation
    
    Returns:
    --------
    result : any
        Task result
    
    Example:
    --------
    def my_task(progress):
        for i in range(100):
            progress(i, f"Processing item {i}", f"{i}% complete")
            time.sleep(0.01)
        return "Done!"
    
    result = run_with_progress(root, my_task, "Loading Data")
    """
    task = BackgroundTask(parent, task_func, title, cancelable)
    return task.run()
