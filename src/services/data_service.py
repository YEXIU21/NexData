"""
Data Service
Handles data loading, saving, and import/export operations
Extracted from main_window.py to improve code organization
"""

import pandas as pd
import os
from tkinter import messagebox


class DataService:
    """Service class for data import/export operations"""
    
    def __init__(self):
        self.supported_formats = {
            'csv': ['.csv'],
            'excel': ['.xlsx', '.xls'],
            'json': ['.json'],
            'parquet': ['.parquet']
        }
    
    def import_csv(self, file_path, encoding='utf-8'):
        """
        Import CSV file
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding (default: utf-8)
            
        Returns:
            DataFrame: Loaded data
        """
        try:
            # Try with specified encoding
            df = pd.read_csv(file_path, encoding=encoding)
            return df
            
        except UnicodeDecodeError:
            # Fallback to latin-1 encoding
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
                return df
            except Exception as e:
                raise ValueError(f"Error reading CSV with latin-1 encoding: {str(e)}")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
            
        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty")
            
        except Exception as e:
            raise ValueError(f"Error importing CSV: {str(e)}")
    
    def import_excel(self, file_path, sheet_name=0):
        """
        Import Excel file
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index (default: 0)
            
        Returns:
            DataFrame: Loaded data
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
            
        except ValueError as e:
            if "Worksheet" in str(e):
                raise ValueError(f"Sheet '{sheet_name}' not found in Excel file")
            raise ValueError(f"Error importing Excel: {str(e)}")
            
        except Exception as e:
            raise ValueError(f"Error importing Excel: {str(e)}")
    
    def import_json(self, file_path):
        """
        Import JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            DataFrame: Loaded data
        """
        try:
            df = pd.read_json(file_path)
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
            
        except ValueError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
            
        except Exception as e:
            raise ValueError(f"Error importing JSON: {str(e)}")
    
    def import_parquet(self, file_path):
        """
        Import Parquet file
        
        Args:
            file_path: Path to Parquet file
            
        Returns:
            DataFrame: Loaded data
        """
        try:
            df = pd.read_parquet(file_path)
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
            
        except Exception as e:
            raise ValueError(f"Error importing Parquet: {str(e)}")
    
    def export_csv(self, df, file_path, index=False, encoding='utf-8'):
        """
        Export to CSV
        
        Args:
            df: DataFrame to export
            file_path: Output file path
            index: Include index (default: False)
            encoding: File encoding (default: utf-8)
            
        Returns:
            bool: True if successful
        """
        try:
            df.to_csv(file_path, index=index, encoding=encoding)
            return True
            
        except PermissionError:
            raise PermissionError(f"Permission denied: {file_path}. File may be open in another program.")
            
        except Exception as e:
            raise ValueError(f"Error exporting CSV: {str(e)}")
    
    def export_excel(self, df, file_path, sheet_name='Sheet1', index=False):
        """
        Export to Excel
        
        Args:
            df: DataFrame to export
            file_path: Output file path
            sheet_name: Sheet name (default: Sheet1)
            index: Include index (default: False)
            
        Returns:
            bool: True if successful
        """
        try:
            df.to_excel(file_path, sheet_name=sheet_name, index=index, engine='openpyxl')
            return True
            
        except PermissionError:
            raise PermissionError(f"Permission denied: {file_path}. File may be open in another program.")
            
        except Exception as e:
            raise ValueError(f"Error exporting Excel: {str(e)}")
    
    def export_json(self, df, file_path, orient='records', indent=2):
        """
        Export to JSON
        
        Args:
            df: DataFrame to export
            file_path: Output file path
            orient: JSON orientation (default: records)
            indent: Indentation spaces (default: 2)
            
        Returns:
            bool: True if successful
        """
        try:
            df.to_json(file_path, orient=orient, indent=indent)
            return True
            
        except Exception as e:
            raise ValueError(f"Error exporting JSON: {str(e)}")
    
    def export_parquet(self, df, file_path):
        """
        Export to Parquet
        
        Args:
            df: DataFrame to export
            file_path: Output file path
            
        Returns:
            bool: True if successful
        """
        try:
            df.to_parquet(file_path, index=False)
            return True
            
        except Exception as e:
            raise ValueError(f"Error exporting Parquet: {str(e)}")
    
    def get_excel_sheet_names(self, file_path):
        """
        Get list of sheet names from Excel file
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            list: Sheet names
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
            
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def validate_file_path(self, file_path):
        """
        Validate file path and extension
        
        Args:
            file_path: Path to validate
            
        Returns:
            tuple: (is_valid, file_type, error_message)
        """
        if not os.path.exists(file_path):
            return False, None, "File does not exist"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        for file_type, extensions in self.supported_formats.items():
            if file_ext in extensions:
                return True, file_type, None
        
        return False, None, f"Unsupported file format: {file_ext}"
    
    def get_file_info(self, file_path):
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: File information
        """
        try:
            stat_info = os.stat(file_path)
            
            info = {
                'name': os.path.basename(file_path),
                'size_bytes': stat_info.st_size,
                'size_mb': stat_info.st_size / (1024 * 1024),
                'modified': stat_info.st_mtime,
                'extension': os.path.splitext(file_path)[1].lower()
            }
            
            return info
            
        except Exception as e:
            raise ValueError(f"Error getting file info: {str(e)}")
    
    def import_file(self, file_path, **kwargs):
        """
        Auto-detect and import file based on extension
        
        Args:
            file_path: Path to file
            **kwargs: Additional arguments for specific import functions
            
        Returns:
            DataFrame: Loaded data
        """
        is_valid, file_type, error = self.validate_file_path(file_path)
        
        if not is_valid:
            raise ValueError(error)
        
        if file_type == 'csv':
            return self.import_csv(file_path, **kwargs)
        elif file_type == 'excel':
            return self.import_excel(file_path, **kwargs)
        elif file_type == 'json':
            return self.import_json(file_path)
        elif file_type == 'parquet':
            return self.import_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def export_file(self, df, file_path, **kwargs):
        """
        Auto-detect and export file based on extension
        
        Args:
            df: DataFrame to export
            file_path: Output file path
            **kwargs: Additional arguments for specific export functions
            
        Returns:
            bool: True if successful
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            return self.export_csv(df, file_path, **kwargs)
        elif file_ext in ['.xlsx', '.xls']:
            return self.export_excel(df, file_path, **kwargs)
        elif file_ext == '.json':
            return self.export_json(df, file_path, **kwargs)
        elif file_ext == '.parquet':
            return self.export_parquet(df, file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported export format: {file_ext}")
    
    def create_backup(self, df, original_path):
        """
        Create backup of current dataframe
        
        Args:
            df: DataFrame to backup
            original_path: Original file path
            
        Returns:
            str: Backup file path
        """
        try:
            if original_path:
                base_name = os.path.splitext(original_path)[0]
                backup_path = f"{base_name}_backup.csv"
                
                df.to_csv(backup_path, index=False)
                return backup_path
            
            return None
            
        except Exception as e:
            raise ValueError(f"Error creating backup: {str(e)}")
    
    def optimize_dataframe_memory(self, df):
        """
        Optimize dataframe memory usage
        
        Args:
            df: DataFrame to optimize
            
        Returns:
            DataFrame: Optimized dataframe
        """
        try:
            df_optimized = df.copy()
            
            # Optimize integer columns
            for col in df_optimized.select_dtypes(include=['int']).columns:
                df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='integer')
            
            # Optimize float columns
            for col in df_optimized.select_dtypes(include=['float']).columns:
                df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
            
            # Convert low-cardinality object columns to category
            for col in df_optimized.select_dtypes(include=['object']).columns:
                num_unique = df_optimized[col].nunique()
                num_total = len(df_optimized[col])
                
                if num_unique / num_total < 0.5:  # If less than 50% unique
                    df_optimized[col] = df_optimized[col].astype('category')
            
            return df_optimized
            
        except Exception as e:
            raise ValueError(f"Error optimizing memory: {str(e)}")
