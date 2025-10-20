"""
Visualization Manager
Handles chart creation and display
Extracted from main_window.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns


class VisualizationManager:
    """Manages data visualizations"""
    
    def __init__(self, app):
        """
        Initialize Visualization Manager
        
        Args:
            app: Reference to main application
        """
        self.app = app
    
    def create_plot(self, plot_type='bar', **kwargs):
        """
        Create a plot with specified type and parameters
        
        Args:
            plot_type: Type of plot ('bar', 'line', 'pie', etc.)
            **kwargs: Additional plot-specific parameters
        """
        if self.app.df is None:
            messagebox.showwarning("Warning", "No data loaded!")
            return
        
        # Create visualization window
        viz_window = tk.Toplevel(self.app.root)
        viz_window.title(f"{plot_type.capitalize()} Chart")
        viz_window.geometry("900x700")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get column selection based on plot type
        columns = list(self.app.df.columns)
        numeric_cols = list(self.app.df.select_dtypes(include=['number']).columns)
        
        # Configuration frame
        config_frame = ttk.Frame(viz_window)
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Column selectors based on plot type
        if plot_type in ['bar', 'line']:
            ttk.Label(config_frame, text="X-axis:").pack(side=tk.LEFT, padx=5)
            x_var = tk.StringVar(value=columns[0] if columns else "")
            x_combo = ttk.Combobox(config_frame, textvariable=x_var, values=columns, width=20)
            x_combo.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(config_frame, text="Y-axis:").pack(side=tk.LEFT, padx=5)
            y_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else "")
            y_combo = ttk.Combobox(config_frame, textvariable=y_var, values=numeric_cols, width=20)
            y_combo.pack(side=tk.LEFT, padx=5)
            
        elif plot_type == 'pie':
            ttk.Label(config_frame, text="Category:").pack(side=tk.LEFT, padx=5)
            cat_var = tk.StringVar(value=columns[0] if columns else "")
            cat_combo = ttk.Combobox(config_frame, textvariable=cat_var, values=columns, width=20)
            cat_combo.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(config_frame, text="Values:").pack(side=tk.LEFT, padx=5)
            val_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else "")
            val_combo = ttk.Combobox(config_frame, textvariable=val_var, values=numeric_cols, width=20)
            val_combo.pack(side=tk.LEFT, padx=5)
            
        elif plot_type in ['histogram', 'boxplot', 'distribution']:
            ttk.Label(config_frame, text="Column:").pack(side=tk.LEFT, padx=5)
            col_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else "")
            col_combo = ttk.Combobox(config_frame, textvariable=col_var, values=numeric_cols, width=20)
            col_combo.pack(side=tk.LEFT, padx=5)
            
        elif plot_type == 'scatter':
            ttk.Label(config_frame, text="X-axis:").pack(side=tk.LEFT, padx=5)
            x_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else "")
            x_combo = ttk.Combobox(config_frame, textvariable=x_var, values=numeric_cols, width=20)
            x_combo.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(config_frame, text="Y-axis:").pack(side=tk.LEFT, padx=5)
            y_var = tk.StringVar(value=numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0] if numeric_cols else "")
            y_combo = ttk.Combobox(config_frame, textvariable=y_var, values=numeric_cols, width=20)
            y_combo.pack(side=tk.LEFT, padx=5)
            
        elif plot_type == 'heatmap':
            # Heatmap uses all numeric columns
            pass
        
        # Canvas for plot
        canvas_frame = ttk.Frame(viz_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        def update_plot():
            """Update the plot with current selections"""
            ax.clear()
            
            try:
                if plot_type == 'bar':
                    x_data = self.app.df[x_var.get()]
                    y_data = self.app.df[y_var.get()]
                    ax.bar(x_data, y_data)
                    ax.set_xlabel(x_var.get())
                    ax.set_ylabel(y_var.get())
                    ax.set_title(f"{y_var.get()} by {x_var.get()}")
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                    
                elif plot_type == 'line':
                    x_data = self.app.df[x_var.get()]
                    y_data = self.app.df[y_var.get()]
                    ax.plot(x_data, y_data, marker='o')
                    ax.set_xlabel(x_var.get())
                    ax.set_ylabel(y_var.get())
                    ax.set_title(f"{y_var.get()} over {x_var.get()}")
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                    
                elif plot_type == 'pie':
                    data = self.app.df.groupby(cat_var.get())[val_var.get()].sum()
                    ax.pie(data.values, labels=data.index, autopct='%1.1f%%')
                    ax.set_title(f"{val_var.get()} distribution by {cat_var.get()}")
                    
                elif plot_type == 'histogram':
                    data = self.app.df[col_var.get()].dropna()
                    ax.hist(data, bins=30, edgecolor='black')
                    ax.set_xlabel(col_var.get())
                    ax.set_ylabel('Frequency')
                    ax.set_title(f"Distribution of {col_var.get()}")
                    
                elif plot_type == 'boxplot':
                    data = self.app.df[col_var.get()].dropna()
                    ax.boxplot(data)
                    ax.set_ylabel(col_var.get())
                    ax.set_title(f"Box Plot of {col_var.get()}")
                    
                elif plot_type == 'scatter':
                    x_data = self.app.df[x_var.get()].dropna()
                    y_data = self.app.df[y_var.get()].dropna()
                    ax.scatter(x_data, y_data, alpha=0.5)
                    ax.set_xlabel(x_var.get())
                    ax.set_ylabel(y_var.get())
                    ax.set_title(f"{y_var.get()} vs {x_var.get()}")
                    
                elif plot_type == 'heatmap':
                    numeric_df = self.app.df.select_dtypes(include=['number'])
                    corr = numeric_df.corr()
                    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
                    ax.set_title("Correlation Heatmap")
                    
                elif plot_type == 'distribution':
                    data = self.app.df[col_var.get()].dropna()
                    sns.histplot(data, kde=True, ax=ax)
                    ax.set_xlabel(col_var.get())
                    ax.set_title(f"Distribution of {col_var.get()}")
                
                fig.tight_layout()
                canvas.draw()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create plot:\n{str(e)}")
        
        # Plot button
        ttk.Button(config_frame, text="Generate Plot", command=update_plot, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        
        # Initial plot
        update_plot()
