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
    
    @staticmethod
    def show_boxplot_dialog(parent, df, create_plot_callback):
        """
        Show boxplot creation dialog
        
        Args:
            parent: Parent window
            df: DataFrame to visualize
            create_plot_callback: Callback function(plot_func)
        """
        import matplotlib.pyplot as plt
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns!")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Create Box Plot")
        dialog.geometry("500x500")
        
        ttk.Label(dialog, text="Create Box Plot - Advanced", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Column selection
        ttk.Label(dialog, text="Select columns to plot:", 
                 font=('Arial', 10, 'bold')).pack(pady=(10,5))
        
        # Listbox for multi-column selection
        list_frame = ttk.Frame(dialog)
        list_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=20)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        col_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, 
                                yscrollcommand=scrollbar.set, height=6)
        col_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=col_listbox.yview)
        
        for col in numeric_cols:
            col_listbox.insert(tk.END, col)
        
        # Select all by default
        col_listbox.select_set(0, tk.END)
        
        # Quick select buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=5)
        
        def select_all():
            col_listbox.select_set(0, tk.END)
        
        def clear_all():
            col_listbox.selection_clear(0, tk.END)
        
        ttk.Button(btn_frame, text="Select All", command=select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All", command=clear_all).pack(side=tk.LEFT, padx=5)
        
        # Orientation
        ttk.Label(dialog, text="Orientation:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        orientation_var = tk.StringVar(value="vertical")
        orient_frame = ttk.Frame(dialog)
        orient_frame.pack(pady=5)
        
        ttk.Radiobutton(orient_frame, text="Vertical", 
                       variable=orientation_var, value="vertical").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(orient_frame, text="Horizontal", 
                       variable=orientation_var, value="horizontal").pack(side=tk.LEFT, padx=20)
        
        # Display options
        ttk.Label(dialog, text="Display options:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        show_means_var = tk.BooleanVar(value=False)
        show_outliers_var = tk.BooleanVar(value=True)
        show_notch_var = tk.BooleanVar(value=False)
        
        opt_frame = ttk.Frame(dialog)
        opt_frame.pack(pady=5)
        
        ttk.Checkbutton(opt_frame, text="Show means", 
                       variable=show_means_var).pack(anchor='w', padx=50)
        ttk.Checkbutton(opt_frame, text="Show outliers", 
                       variable=show_outliers_var).pack(anchor='w', padx=50)
        ttk.Checkbutton(opt_frame, text="Show notch (confidence interval)", 
                       variable=show_notch_var).pack(anchor='w', padx=50)
        
        # Color
        ttk.Label(dialog, text="Box color:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        color_var = tk.StringVar(value="lightblue")
        color_frame = ttk.Frame(dialog)
        color_frame.pack(pady=5)
        
        colors = [("Light Blue", "lightblue"), ("Light Green", "lightgreen"), 
                  ("Light Coral", "lightcoral"), ("Light Gray", "lightgray")]
        
        for i, (name, color) in enumerate(colors):
            ttk.Radiobutton(color_frame, text=name, variable=color_var, 
                           value=color).grid(row=0, column=i, padx=10)
        
        # Title
        ttk.Label(dialog, text="Chart title (optional):", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        title_var = tk.StringVar(value="")
        ttk.Entry(dialog, textvariable=title_var, width=40).pack(pady=5)
        
        def plot():
            selected_indices = col_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Warning", "Please select at least one column!")
                return
            
            selected_cols = [col_listbox.get(i) for i in selected_indices]
            
            try:
                orientation = orientation_var.get()
                vert = (orientation == "vertical")
                chart_title = title_var.get() if title_var.get() else 'Box Plot - Distribution Comparison'
                color = color_var.get()
                
                def plot_func(fig, ax):
                    data_to_plot = [df[col].dropna() for col in selected_cols]
                    
                    bp = ax.boxplot(data_to_plot, labels=selected_cols, 
                                   vert=vert, patch_artist=True,
                                   showmeans=show_means_var.get(),
                                   showfliers=show_outliers_var.get(),
                                   notch=show_notch_var.get())
                    
                    # Color the boxes
                    for patch in bp['boxes']:
                        patch.set_facecolor(color)
                        patch.set_alpha(0.7)
                    
                    # Style medians
                    for median in bp['medians']:
                        median.set_color('red')
                        median.set_linewidth(2)
                    
                    # Style means if shown
                    if show_means_var.get():
                        for mean in bp['means']:
                            mean.set_marker('D')
                            mean.set_markerfacecolor('green')
                            mean.set_markersize(6)
                    
                    ax.set_title(chart_title, fontsize=14, fontweight='bold')
                    
                    if vert:
                        ax.set_ylabel('Values', fontsize=11)
                        ax.grid(True, alpha=0.3, axis='y')
                        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                    else:
                        ax.set_xlabel('Values', fontsize=11)
                        ax.grid(True, alpha=0.3, axis='x')
                
                create_plot_callback(plot_func)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Box plot creation failed:\n{str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Create Plot", command=plot, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_scatter_plot_dialog(parent, df, create_plot_callback):
        """
        Show scatter plot creation dialog
        
        Args:
            parent: Parent window
            df: DataFrame to visualize
            create_plot_callback: Callback function(plot_func)
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            messagebox.showwarning("Warning", "Need at least 2 numeric columns!")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Create Scatter Plot")
        dialog.geometry("520x550")
        
        ttk.Label(dialog, text="Create Scatter Plot - Advanced", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # X and Y axis selection
        axis_frame = ttk.Frame(dialog)
        axis_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Label(axis_frame, text="X axis:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        x_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(axis_frame, textvariable=x_var, values=numeric_cols, 
                    state='readonly', width=30).grid(row=0, column=1, padx=10)
        
        ttk.Label(axis_frame, text="Y axis:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        y_var = tk.StringVar(value=numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])
        ttk.Combobox(axis_frame, textvariable=y_var, values=numeric_cols, 
                    state='readonly', width=30).grid(row=1, column=1, padx=10)
        
        # Color by category
        ttk.Label(dialog, text="Color by category (optional):", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        color_by_var = tk.StringVar(value="None")
        ttk.Combobox(dialog, textvariable=color_by_var, 
                    values=["None"] + list(df.columns), 
                    state='readonly', width=35).pack(pady=5)
        
        # Marker customization
        ttk.Label(dialog, text="Marker style:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        marker_frame = ttk.Frame(dialog)
        marker_frame.pack(pady=5)
        
        marker_var = tk.StringVar(value="o")
        markers = [("Circle", "o"), ("Square", "s"), ("Triangle", "^"), 
                   ("Diamond", "D"), ("Star", "*"), ("Plus", "+")]
        
        for i, (name, marker) in enumerate(markers):
            ttk.Radiobutton(marker_frame, text=name, variable=marker_var, 
                           value=marker).grid(row=i//3, column=i%3, padx=15, pady=2)
        
        # Size and transparency
        size_frame = ttk.Frame(dialog)
        size_frame.pack(pady=10)
        
        ttk.Label(size_frame, text="Marker size:", font=('Arial', 9)).grid(row=0, column=0, padx=5)
        size_var = tk.IntVar(value=50)
        ttk.Spinbox(size_frame, from_=10, to=200, textvariable=size_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(size_frame, text="Transparency:", font=('Arial', 9)).grid(row=0, column=2, padx=5)
        alpha_var = tk.DoubleVar(value=0.6)
        ttk.Spinbox(size_frame, from_=0.1, to=1.0, increment=0.1, textvariable=alpha_var, width=10).grid(row=0, column=3, padx=5)
        
        # Display options
        ttk.Label(dialog, text="Display options:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        show_trend_var = tk.BooleanVar(value=False)
        show_correlation_var = tk.BooleanVar(value=False)
        
        opt_frame = ttk.Frame(dialog)
        opt_frame.pack(pady=5)
        
        ttk.Checkbutton(opt_frame, text="Show trend line", 
                       variable=show_trend_var).pack(anchor='w', padx=50)
        ttk.Checkbutton(opt_frame, text="Show correlation coefficient", 
                       variable=show_correlation_var).pack(anchor='w', padx=50)
        
        # Title
        ttk.Label(dialog, text="Chart title (optional):", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        title_var = tk.StringVar(value="")
        ttk.Entry(dialog, textvariable=title_var, width=40).pack(pady=5)
        
        def plot():
            x_col = x_var.get()
            y_col = y_var.get()
            color_by = color_by_var.get()
            
            try:
                chart_title = title_var.get() if title_var.get() else f'{y_col} vs {x_col}'
                marker = marker_var.get()
                size = size_var.get()
                alpha = alpha_var.get()
                
                def plot_func(fig, ax):
                    # Prepare data
                    if color_by != "None":
                        # Color by category
                        categories = df[color_by].unique()
                        for cat in categories:
                            mask = df[color_by] == cat
                            ax.scatter(df[mask][x_col], df[mask][y_col], 
                                      label=cat, alpha=alpha, s=size, marker=marker)
                        ax.legend()
                    else:
                        # Single color
                        ax.scatter(df[x_col], df[y_col], 
                                  alpha=alpha, s=size, marker=marker, color='steelblue')
                    
                    # Trend line
                    if show_trend_var.get():
                        x_data = df[x_col].dropna()
                        y_data = df[y_col].dropna()
                        z = np.polyfit(x_data, y_data, 1)
                        p = np.poly1d(z)
                        ax.plot(x_data, p(x_data), "r--", linewidth=2, label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}')
                        ax.legend()
                    
                    # Correlation coefficient
                    if show_correlation_var.get():
                        corr = df[[x_col, y_col]].corr().iloc[0, 1]
                        ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                               transform=ax.transAxes, fontsize=10, 
                               verticalalignment='top', 
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                    
                    ax.set_title(chart_title, fontsize=14, fontweight='bold')
                    ax.set_xlabel(x_col, fontsize=11)
                    ax.set_ylabel(y_col, fontsize=11)
                    ax.grid(True, alpha=0.3)
                
                create_plot_callback(plot_func)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Scatter plot creation failed:\n{str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Create Plot", command=plot, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_pie_chart_dialog(parent, df, create_plot_callback):
        """
        Show pie chart creation dialog
        
        Args:
            parent: Parent window
            df: DataFrame to visualize
            create_plot_callback: Callback function(plot_func)
        """
        import matplotlib.pyplot as plt
        
        dialog = tk.Toplevel(parent)
        dialog.title("Create Pie Chart")
        dialog.geometry("500x500")
        
        ttk.Label(dialog, text="Create Pie Chart - Advanced", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Column selection (all columns now allowed)
        ttk.Label(dialog, text="Select column:", font=('Arial', 10, 'bold')).pack(pady=(10,5))
        col_var = tk.StringVar(value=df.columns[0])
        ttk.Combobox(dialog, textvariable=col_var, values=list(df.columns), 
                    state='readonly', width=35).pack(pady=5)
        
        # Number of slices
        ttk.Label(dialog, text="Number of slices to show:", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        slice_frame = ttk.Frame(dialog)
        slice_frame.pack(pady=5)
        
        ttk.Label(slice_frame, text="Top").pack(side=tk.LEFT, padx=5)
        slice_var = tk.IntVar(value=10)
        ttk.Spinbox(slice_frame, from_=3, to=20, textvariable=slice_var, width=10).pack(side=tk.LEFT)
        ttk.Label(slice_frame, text="categories (others grouped as 'Other')").pack(side=tk.LEFT, padx=5)
        
        # Chart title
        ttk.Label(dialog, text="Chart title (optional):", 
                 font=('Arial', 10, 'bold')).pack(pady=(15,5))
        title_var = tk.StringVar(value="")
        ttk.Entry(dialog, textvariable=title_var, width=40).pack(pady=5)
        
        # Color scheme
        ttk.Label(dialog, text="Color scheme:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        color_var = tk.StringVar(value="default")
        color_frame = ttk.Frame(dialog)
        color_frame.pack(pady=5)
        
        ttk.Radiobutton(color_frame, text="Default", 
                       variable=color_var, value="default").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(color_frame, text="Pastel", 
                       variable=color_var, value="pastel").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(color_frame, text="Bold", 
                       variable=color_var, value="bold").grid(row=0, column=2, padx=10)
        ttk.Radiobutton(color_frame, text="Blues", 
                       variable=color_var, value="blues").grid(row=1, column=0, padx=10)
        ttk.Radiobutton(color_frame, text="Greens", 
                       variable=color_var, value="greens").grid(row=1, column=1, padx=10)
        ttk.Radiobutton(color_frame, text="Reds", 
                       variable=color_var, value="reds").grid(row=1, column=2, padx=10)
        
        # Display options
        ttk.Label(dialog, text="Display options:", font=('Arial', 10, 'bold')).pack(pady=(15,5))
        
        show_percent_var = tk.BooleanVar(value=True)
        show_values_var = tk.BooleanVar(value=False)
        explode_largest_var = tk.BooleanVar(value=False)
        
        opt_frame = ttk.Frame(dialog)
        opt_frame.pack(pady=5)
        
        ttk.Checkbutton(opt_frame, text="Show percentages", 
                       variable=show_percent_var).pack(anchor='w', padx=50)
        ttk.Checkbutton(opt_frame, text="Show actual values", 
                       variable=show_values_var).pack(anchor='w', padx=50)
        ttk.Checkbutton(opt_frame, text="Explode largest slice", 
                       variable=explode_largest_var).pack(anchor='w', padx=50)
        
        def plot():
            col = col_var.get()
            n_slices = slice_var.get()
            
            try:
                # Get value counts
                value_counts = df[col].value_counts()
                
                # Limit to top N and group others
                if len(value_counts) > n_slices:
                    top_values = value_counts.head(n_slices)
                    others_sum = value_counts.iloc[n_slices:].sum()
                    top_values['Other'] = others_sum
                    value_counts = top_values
                
                # Color schemes
                color_schemes = {
                    'default': None,  # matplotlib default
                    'pastel': plt.cm.Pastel1(range(len(value_counts))),
                    'bold': plt.cm.Set1(range(len(value_counts))),
                    'blues': plt.cm.Blues(np.linspace(0.4, 0.8, len(value_counts))),
                    'greens': plt.cm.Greens(np.linspace(0.4, 0.8, len(value_counts))),
                    'reds': plt.cm.Reds(np.linspace(0.4, 0.8, len(value_counts)))
                }
                
                colors = color_schemes.get(color_var.get())
                
                # Explode options
                explode = None
                if explode_largest_var.get():
                    explode = [0.1 if i == 0 else 0 for i in range(len(value_counts))]
                
                # Format percentages and/or values
                autopct_format = None
                if show_percent_var.get() and show_values_var.get():
                    autopct_format = lambda pct: f'{pct:.1f}%\n({int(pct/100*value_counts.sum())})'
                elif show_percent_var.get():
                    autopct_format = '%1.1f%%'
                elif show_values_var.get():
                    autopct_format = lambda pct: f'{int(pct/100*value_counts.sum())}'
                
                # Chart title
                chart_title = title_var.get() if title_var.get() else f'Distribution of {col}'
                
                def plot_func(fig, ax):
                    wedges, texts, autotexts = ax.pie(
                        value_counts.values, 
                        labels=value_counts.index, 
                        autopct=autopct_format,
                        startangle=90,
                        colors=colors,
                        explode=explode,
                        shadow=explode_largest_var.get()
                    )
                    
                    # Style the text
                    for text in texts:
                        text.set_fontsize(10)
                    
                    if autotexts:
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_fontsize(9)
                            autotext.set_fontweight('bold')
                    
                    ax.set_title(chart_title, fontsize=14, fontweight='bold', pad=20)
                    ax.axis('equal')
                
                create_plot_callback(plot_func)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Pie chart creation failed:\n{str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Create Chart", command=plot, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def show_bar_chart_dialog(parent, df, create_plot_callback):
        """Show bar chart creation dialog"""
        import matplotlib.pyplot as plt
        
        dialog = tk.Toplevel(parent)
        dialog.title("Create Bar Chart")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="X-axis (Categories):", font=('Arial', 11, 'bold')).pack(pady=5)
        x_var = tk.StringVar(value=df.columns[0])
        ttk.Combobox(dialog, textvariable=x_var, values=list(df.columns), 
                     state='readonly', width=30).pack(pady=5)
        
        ttk.Label(dialog, text="Y-axis (Values):", font=('Arial', 11, 'bold')).pack(pady=5)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        y_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else df.columns[0])
        ttk.Combobox(dialog, textvariable=y_var, values=list(df.columns), 
                     state='readonly', width=30).pack(pady=5)
        
        ttk.Label(dialog, text="Chart Title (optional):", font=('Arial', 11, 'bold')).pack(pady=5)
        title_var = tk.StringVar(value="")
        ttk.Entry(dialog, textvariable=title_var, width=33).pack(pady=5)
        
        def plot():
            x_col = x_var.get()
            y_col = y_var.get()
            title = title_var.get() or f"{y_col} by {x_col}"
            
            try:
                import pandas as pd
                # Aggregate data if needed (group by x, sum y)
                if df[x_col].duplicated().any():
                    plot_data = df.groupby(x_col)[y_col].sum().sort_values(ascending=False)
                else:
                    plot_data = df.set_index(x_col)[y_col].sort_values(ascending=False)
                
                def plot_func(fig, ax):
                    plot_data.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
                    ax.set_title(title, fontsize=14, fontweight='bold')
                    ax.set_xlabel(x_col, fontsize=11)
                    ax.set_ylabel(y_col, fontsize=11)
                    ax.grid(True, alpha=0.3, axis='y')
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                create_plot_callback(plot_func)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Bar chart creation failed:\n{str(e)}")
        
        ttk.Button(dialog, text="Create Chart", command=plot).pack(pady=15)
    
    @staticmethod
    def show_line_chart_dialog(parent, df, create_plot_callback):
        """Show line chart creation dialog"""
        import matplotlib.pyplot as plt
        import pandas as pd
        
        dialog = tk.Toplevel(parent)
        dialog.title("Create Line Chart")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="X-axis (usually date/time):", font=('Arial', 11, 'bold')).pack(pady=5)
        x_var = tk.StringVar(value=df.columns[0])
        ttk.Combobox(dialog, textvariable=x_var, values=list(df.columns), 
                     state='readonly', width=30).pack(pady=5)
        
        ttk.Label(dialog, text="Y-axis (Values):", font=('Arial', 11, 'bold')).pack(pady=5)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        y_var = tk.StringVar(value=numeric_cols[0] if numeric_cols else df.columns[0])
        ttk.Combobox(dialog, textvariable=y_var, values=list(df.columns), 
                     state='readonly', width=30).pack(pady=5)
        
        ttk.Label(dialog, text="Chart Title (optional):", font=('Arial', 11, 'bold')).pack(pady=5)
        title_var = tk.StringVar(value="")
        ttk.Entry(dialog, textvariable=title_var, width=33).pack(pady=5)
        
        def plot():
            x_col = x_var.get()
            y_col = y_var.get()
            title = title_var.get() or f"{y_col} over {x_col}"
            
            try:
                # Try to convert x to datetime if it looks like dates
                df_temp = df[[x_col, y_col]].copy()
                try:
                    df_temp[x_col] = pd.to_datetime(df_temp[x_col])
                    df_temp = df_temp.sort_values(x_col)
                except:
                    pass  # Not a date column, use as is
                
                def plot_func(fig, ax):
                    ax.plot(df_temp[x_col], df_temp[y_col], marker='o', linestyle='-', 
                           linewidth=2, markersize=5, color='steelblue')
                    ax.set_title(title, fontsize=14, fontweight='bold')
                    ax.set_xlabel(x_col, fontsize=11)
                    ax.set_ylabel(y_col, fontsize=11)
                    ax.grid(True, alpha=0.3)
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                create_plot_callback(plot_func)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Line chart creation failed:\n{str(e)}")
        
        ttk.Button(dialog, text="Create Chart", command=plot).pack(pady=15)
    
    @staticmethod
    def show_distribution_plot_dialog(parent, df, create_plot_callback):
        """Show distribution plot dialog"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Warning", "No numeric columns!")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Distribution Plot")
        ttk.Label(dialog, text="Select column:").pack(pady=10)
        col_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(dialog, textvariable=col_var, values=numeric_cols, state='readonly').pack(pady=5)
        
        def plot():
            col = col_var.get()
            def plot_func(fig, ax):
                data = df[col].dropna()
                # Histogram using matplotlib
                ax.hist(data, bins=30, alpha=0.7, edgecolor='black', density=True, label='Histogram')
                # KDE using scipy
                from scipy.stats import gaussian_kde
                kde = gaussian_kde(data)
                x_range = np.linspace(data.min(), data.max(), 200)
                ax.plot(x_range, kde(x_range), color='red', linewidth=2, label='KDE')
                ax.set_title(f'Distribution of {col}', fontsize=14, fontweight='bold')
                ax.set_xlabel(col)
                ax.set_ylabel('Density')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            create_plot_callback(plot_func)
            dialog.destroy()
        
        ttk.Button(dialog, text="Plot", command=plot).pack(pady=10)
