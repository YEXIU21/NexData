"""
Chart Creation Module
All visualization and chart generation functions

SEPARATION OF CONCERNS: Only chart/plot creation logic
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import numpy as np


class ChartCreator:
    """Creates various types of charts"""
    
    @staticmethod
    def create_histogram(data, column, bins=30, title=None):
        """Create histogram"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        data[column].hist(ax=ax, bins=bins, edgecolor='black', alpha=0.7)
        ax.set_title(title or f'Distribution of {column}', fontsize=14, fontweight='bold')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    @staticmethod
    def create_boxplot(data, columns=None):
        """Create box plot"""
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        data[columns].boxplot(ax=ax)
        ax.set_title('Box Plot - Distribution Comparison', fontsize=14, fontweight='bold')
        ax.set_ylabel('Values')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        return fig
    
    @staticmethod
    def create_scatter(data, x_col, y_col, title=None):
        """Create scatter plot"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        data.plot.scatter(x=x_col, y=y_col, ax=ax, alpha=0.6, s=50)
        ax.set_title(title or f'{y_col} vs {x_col}', fontsize=14, fontweight='bold')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(True, alpha=0.3)
        
        return fig
    
    @staticmethod
    def create_bar_chart(data, x_col, y_col=None, title=None):
        """Create bar chart"""
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        if y_col:
            data.plot.bar(x=x_col, y=y_col, ax=ax)
        else:
            value_counts = data[x_col].value_counts().head(10)
            value_counts.plot.bar(ax=ax)
        
        ax.set_title(title or f'Bar Chart - {x_col}', fontsize=14, fontweight='bold')
        ax.set_xlabel(x_col)
        ax.set_ylabel('Count' if not y_col else y_col)
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        return fig
    
    @staticmethod
    def create_line_chart(data, x_col, y_col, title=None):
        """Create line chart"""
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(data[x_col], data[y_col], marker='o', linestyle='-', linewidth=2, markersize=4)
        ax.set_title(title or f'{y_col} over {x_col}', fontsize=14, fontweight='bold')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.grid(True, alpha=0.3)
        
        return fig
    
    @staticmethod
    def create_pie_chart(data, column, top_n=10, title=None):
        """Create pie chart"""
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        value_counts = data[column].value_counts().head(top_n)
        ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_title(title or f'Distribution of {column}', fontsize=14, fontweight='bold')
        
        return fig
    
    @staticmethod
    def create_heatmap(correlation_matrix, title='Correlation Heatmap'):
        """Create correlation heatmap"""
        fig = Figure(figsize=(12, 10), dpi=100)
        ax = fig.add_subplot(111)
        
        sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   ax=ax, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        return fig
    
    @staticmethod
    def create_distribution_plot(data, column, title=None):
        """Create distribution plot with histogram and KDE"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        data[column].hist(ax=ax, bins=30, alpha=0.7, edgecolor='black', 
                         density=True, label='Histogram')
        data[column].plot(kind='kde', ax=ax, color='red', linewidth=2, label='KDE')
        
        ax.set_title(title or f'Distribution of {column}', fontsize=14, fontweight='bold')
        ax.set_xlabel(column)
        ax.set_ylabel('Density')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    @staticmethod
    def create_violin_plot(data, columns=None, title='Violin Plot'):
        """Create violin plot"""
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()[:6]
        
        data_to_plot = [data[col].dropna() for col in columns]
        parts = ax.violinplot(data_to_plot, showmeans=True, showmedians=True)
        
        ax.set_xticks(range(1, len(columns) + 1))
        ax.set_xticklabels(columns, rotation=45, ha='right')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        return fig


class TimeSeriesPlots:
    """Time series specific plots"""
    
    @staticmethod
    def create_time_series_plot(data, date_col, value_col, title=None):
        """Create time series line plot"""
        fig = Figure(figsize=(14, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(data[date_col], data[value_col], marker='o', linestyle='-', 
               linewidth=2, markersize=4)
        ax.set_title(title or f'{value_col} over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel(value_col)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()  # Format x-axis dates nicely
        
        return fig
    
    @staticmethod
    def create_seasonal_plot(data, date_col, value_col, period='M'):
        """Create seasonal decomposition plot"""
        fig = Figure(figsize=(14, 8), dpi=100)
        
        # This is a placeholder - actual seasonal decomposition would require statsmodels
        ax = fig.add_subplot(111)
        ax.plot(data[date_col], data[value_col])
        ax.set_title('Seasonal Analysis (Basic)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel(value_col)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()
        
        return fig
