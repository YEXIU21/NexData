"""
Data Import/Export Operations
Handles all file I/O operations for CSV, Excel, JSON formats

SEPARATION OF CONCERNS: Only data import/export logic
"""

import pandas as pd
import os


class DataImporter:
    """Handles data import operations"""
    
    @staticmethod
    def import_csv(file_path, encodings=['utf-8', 'latin-1', 'cp1252']):
        """Import CSV with multiple encoding support"""
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                return df, None
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return None, str(e)
        return None, "Failed to decode file with supported encodings"
    
    @staticmethod
    def import_excel(file_path, sheet_name=0):
        """Import Excel file"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def import_json(file_path):
        """Import JSON file"""
        try:
            df = pd.read_json(file_path)
            return df, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_excel_sheets(file_path):
        """Get list of sheets in Excel file"""
        try:
            xl_file = pd.ExcelFile(file_path)
            return xl_file.sheet_names, None
        except Exception as e:
            return None, str(e)


class DataExporter:
    """Handles data export operations"""
    
    @staticmethod
    def export_csv(df, file_path):
        """Export to CSV"""
        try:
            df.to_csv(file_path, index=False)
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def export_excel(df, file_path):
        """Export to Excel"""
        try:
            df.to_excel(file_path, index=False, engine='openpyxl')
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def export_json(df, file_path):
        """Export to JSON"""
        try:
            df.to_json(file_path, orient='records', indent=2)
            return True, None
        except Exception as e:
            return False, str(e)
