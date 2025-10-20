"""
Visualization Dialog Factory
Centralized dialog components for data visualization features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np


class VisualizationDialogs:
    """Factory class for all visualization-related dialogs"""
    
    @staticmethod
    def show_histogram_dialog(parent, df, create_plot_callback):
        """
        Show histogram creation dialog
        
        Args:
            parent: Parent window
            df: DataFrame to visualize
            create_plot_callback: Callback function(plot_func)
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns!")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Create Histogram")
        dialog.geometry("500x480")
        
        ttk.Label(dialog, text="Create Histogram - Advanced", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Column selection
        ttk.Label(dialog, text="Select column:", font=('Arial', 10, 'bold')).pack(pady=(10,5))
        col_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(dialog, textvariable=col_var, values=numeric_cols, 
                    state='readonly', width=35).pack(pady=5)
        
        # Bin configuration
        ttk.Label(dialog, text="Bin configuration:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        bin_frame = ttk.Frame(dialog)
        bin_frame.pack(pady=5)
        
        bin_method_var = tk.StringVar(value="manual")
        ttk.Radiobutton(bin_frame, text="Manual:", variable=bin_method_var, 
                       value="manual").grid(row=0, column=0, sticky='w', padx=10)
        
        bin_count_var = tk.IntVar(value=30)
        ttk.Spinbox(bin_frame, from_=5, to=100, textvariable=bin_count_var, 
                   width=10).grid(row=0, column=1, padx=5)
        ttk.Label(bin_frame, text="bins").grid(row=0, column=2, sticky='w')
        
        ttk.Radiobutton(bin_frame, text="Auto (let matplotlib decide)", 
                       variable=bin_method_var, value="auto").grid(row=1, column=0, columnspan=3, 
                                                                    sticky='w', padx=10, pady=5)
        ttk.Radiobutton(bin_frame, text="Sturges' formula (good for normal data)", 
                       variable=bin_method_var, value="sturges").grid(row=2, column=0, columnspan=3, 
                                                                       sticky='w', padx=10, pady=2)
        ttk.Radiobutton(bin_frame, text="Scott's rule (minimizes variance)", 
                       variable=bin_method_var, value="scott").grid(row=3, column=0, columnspan=3, 
                                                                     sticky='w', padx=10, pady=2)
        
        # Color selection
        ttk.Label(dialog, text="Bar color:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        color_var = tk.StringVar(value="steelblue")
        color_frame = ttk.Frame(dialog)
        color_frame.pack(pady=5)
        
        colors = [("Blue", "steelblue"), ("Green", "green"), ("Red", "crimson"),
                  ("Purple", "purple"), ("Orange", "orange"), ("Gray", "gray")]
        
        for i, (name, color) in enumerate(colors):
            ttk.Radiobutton(color_frame, text=name, variable=color_var, 
                           value=color).grid(row=i//3, column=i%3, padx=10, pady=2)
        
        # Display options
        ttk.Label(dialog, text="Display options:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        show_stats_var = tk.BooleanVar(value=False)
        show_normal_var = tk.BooleanVar(value=False)
        show_kde_var = tk.BooleanVar(value=False)
        
        opt_frame = ttk.Frame(dialog)
        opt_frame.pack(pady=5)
        
        ttk.Checkbutton(opt_frame, text="Show statistics (mean, median)", 
                       variable=show_stats_var).pack(anchor='w', padx=50)
        ttk.Checkbutton(opt_frame, text="Overlay normal distribution curve", 
                       variable=show_normal_var).pack(anchor='w', padx=50)
        ttk.Checkbutton(opt_frame, text="Show KDE (Kernel Density Estimate)", 
                       variable=show_kde_var).pack(anchor='w', padx=50)
        
        # Title
        ttk.Label(dialog, text="Chart title (optional):", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        title_var = tk.StringVar(value="")
        ttk.Entry(dialog, textvariable=title_var, width=40).pack(pady=5)
        
        def plot():
            col = col_var.get()
            
            try:
                # Get bin configuration
                bin_method = bin_method_var.get()
                if bin_method == "manual":
                    bins = bin_count_var.get()
                else:
                    bins = bin_method
                
                data = df[col].dropna()
                color = color_var.get()
                chart_title = title_var.get() if title_var.get() else f'Distribution of {col}'
                
                def plot_func(fig, ax):
                    # Create histogram
                    n, bins_arr, patches = ax.hist(data, bins=bins, 
                                                   color=color, edgecolor='black', 
                                                   alpha=0.7, density=show_kde_var.get() or show_normal_var.get())
                    
                    # Show statistics
                    if show_stats_var.get():
                        mean_val = data.mean()
                        median_val = data.median()
                        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
                        ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
                    
                    # Overlay normal distribution
                    if show_normal_var.get():
                        from scipy import stats
                        mu, sigma = data.mean(), data.std()
                        x = np.linspace(data.min(), data.max(), 100)
                        ax.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                               label=f'Normal (μ={mu:.1f}, σ={sigma:.1f})')
                    
                    # Show KDE
                    if show_kde_var.get():
                        from scipy.stats import gaussian_kde
                        kde = gaussian_kde(data)
                        x_range = np.linspace(data.min(), data.max(), 200)
                        ax.plot(x_range, kde(x_range), 'b-', linewidth=2, label='KDE')
                    
                    ax.set_title(chart_title, fontsize=14, fontweight='bold')
                    ax.set_xlabel(col, fontsize=11)
                    ax.set_ylabel('Density' if (show_kde_var.get() or show_normal_var.get()) else 'Frequency', 
                                 fontsize=11)
                    ax.grid(True, alpha=0.3)
                    
                    if show_stats_var.get() or show_normal_var.get() or show_kde_var.get():
                        ax.legend()
                
                create_plot_callback(plot_func)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Histogram creation failed:\n{str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Create Histogram", command=plot, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
