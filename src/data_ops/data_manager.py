"""
Data Manager - Intelligent data handling for enterprise-grade performance
Automatically chooses between in-memory and database storage based on data size
"""

import pandas as pd
from typing import Optional, Tuple, Dict, Any
import logging
from .database import get_data_store

logger = logging.getLogger(__name__)

# Thresholds for automatic mode selection
MEMORY_THRESHOLD_ROWS = 100000  # Above this, use database
MEMORY_THRESHOLD_SIZE_MB = 100  # Above this size, use database


class DataManager:
    """
    Intelligent data manager that automatically handles small and large datasets
    Small data: In-memory pandas
    Large data: Database with pagination
    """
    
    def __init__(self):
        self.current_data = None
        self.current_table = None
        self.use_database = False
        self.data_store = get_data_store()
        self.metadata = {}
    
    def load_data(self, df: pd.DataFrame, source_name: str = "data",
                  force_database: bool = False) -> Tuple[bool, str]:
        """
        Load data intelligently (auto-detect if database needed)
        
        Parameters:
        -----------
        df : pd.DataFrame
            Data to load
        source_name : str
            Name/identifier for this dataset
        force_database : bool
            Force use of database even for small data
        
        Returns:
        --------
        success : bool
        message : str
        """
        try:
            rows, cols = df.shape
            size_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            
            logger.info(f"Loading data: {rows} rows, {cols} cols, {size_mb:.2f} MB")
            
            # Decide storage method
            use_db = force_database or rows > MEMORY_THRESHOLD_ROWS or size_mb > MEMORY_THRESHOLD_SIZE_MB
            
            if use_db:
                # Large dataset - use database
                table_name = f"data_{source_name}".replace(" ", "_").lower()
                success = self.data_store.store_dataframe(df, table_name, if_exists='replace')
                
                if success:
                    self.use_database = True
                    self.current_table = table_name
                    self.current_data = None  # Don't keep in memory
                    self.metadata = {
                        'rows': rows,
                        'cols': cols,
                        'size_mb': size_mb,
                        'columns': list(df.columns),
                        'source': source_name,
                        'storage': 'database'
                    }
                    
                    # Create indexes for common columns
                    self._create_indexes(df, table_name)
                    
                    return True, f"Loaded {rows:,} rows into database (large dataset mode)"
                else:
                    return False, "Failed to store data in database"
            else:
                # Small dataset - keep in memory
                self.use_database = False
                self.current_data = df.copy()
                self.current_table = None
                self.metadata = {
                    'rows': rows,
                    'cols': cols,
                    'size_mb': size_mb,
                    'columns': list(df.columns),
                    'source': source_name,
                    'storage': 'memory'
                }
                
                return True, f"Loaded {rows:,} rows into memory (fast mode)"
        
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False, f"Error loading data: {str(e)}"
    
    def get_data(self, limit: Optional[int] = None, offset: int = 0) -> pd.DataFrame:
        """
        Get data with automatic pagination
        
        Parameters:
        -----------
        limit : int
            Number of rows to retrieve (None = all for memory, 10000 for database)
        offset : int
            Starting row
        
        Returns:
        --------
        df : pd.DataFrame
        """
        try:
            if self.use_database:
                # Database mode - pagination by default
                if limit is None:
                    limit = 10000  # Default limit for database
                return self.data_store.load_dataframe(self.current_table, limit=limit, offset=offset)
            else:
                # Memory mode - return all or sliced
                if self.current_data is None:
                    return pd.DataFrame()
                
                if limit:
                    return self.current_data.iloc[offset:offset+limit].copy()
                else:
                    return self.current_data.copy()
        except Exception as e:
            logger.error(f"Failed to get data: {e}")
            return pd.DataFrame()
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query (database mode only)
        
        Parameters:
        -----------
        sql : str
            SQL query
        
        Returns:
        --------
        df : pd.DataFrame
        """
        if self.use_database:
            return self.data_store.query(sql)
        else:
            logger.warning("SQL queries only available in database mode")
            return pd.DataFrame()
    
    def get_page(self, page_num: int, page_size: int = 1000) -> pd.DataFrame:
        """
        Get specific page of data
        
        Parameters:
        -----------
        page_num : int
            Page number (1-indexed)
        page_size : int
            Rows per page
        
        Returns:
        --------
        df : pd.DataFrame
        """
        offset = (page_num - 1) * page_size
        return self.get_data(limit=page_size, offset=offset)
    
    def get_total_rows(self) -> int:
        """Get total number of rows"""
        if self.use_database:
            row_count, _ = self.data_store.get_table_info(self.current_table)
            return row_count
        elif self.current_data is not None:
            return len(self.current_data)
        else:
            return 0
    
    def get_total_pages(self, page_size: int = 1000) -> int:
        """Calculate total number of pages"""
        total = self.get_total_rows()
        return (total + page_size - 1) // page_size  # Ceiling division
    
    def get_columns(self) -> list:
        """Get list of column names"""
        return self.metadata.get('columns', [])
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get dataset metadata"""
        return self.metadata.copy()
    
    def get_sample(self, n: int = 100) -> pd.DataFrame:
        """
        Get random sample of data
        
        Parameters:
        -----------
        n : int
            Number of rows to sample
        
        Returns:
        --------
        df : pd.DataFrame
        """
        if self.use_database:
            # Database sampling
            total = self.get_total_rows()
            if total <= n:
                return self.get_data(limit=n)
            else:
                sql = f"SELECT * FROM {self.current_table} ORDER BY RANDOM() LIMIT {n}"
                return self.data_store.query(sql)
        else:
            # Memory sampling
            if self.current_data is None:
                return pd.DataFrame()
            if len(self.current_data) <= n:
                return self.current_data.copy()
            return self.current_data.sample(n).copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about the dataset
        
        Returns:
        --------
        stats : dict
        """
        try:
            sample = self.get_sample(10000)  # Sample for stats
            
            if sample.empty:
                return {}
            
            stats = {
                'total_rows': self.get_total_rows(),
                'total_columns': len(self.get_columns()),
                'storage_mode': self.metadata.get('storage', 'unknown'),
                'memory_size_mb': self.metadata.get('size_mb', 0),
                'numeric_columns': len(sample.select_dtypes(include=['number']).columns),
                'text_columns': len(sample.select_dtypes(include=['object']).columns),
                'datetime_columns': len(sample.select_dtypes(include=['datetime']).columns),
                'missing_values': int(sample.isnull().sum().sum()),
            }
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def clear(self):
        """Clear current data"""
        if self.use_database and self.current_table:
            self.data_store.delete_table(self.current_table)
        
        self.current_data = None
        self.current_table = None
        self.use_database = False
        self.metadata = {}
    
    def _create_indexes(self, df: pd.DataFrame, table_name: str):
        """Create indexes on common column types"""
        try:
            # Index datetime columns (for date filtering)
            for col in df.select_dtypes(include=['datetime64']).columns:
                self.data_store.create_index(table_name, col)
            
            # Index ID columns
            for col in df.columns:
                if 'id' in col.lower():
                    self.data_store.create_index(table_name, col)
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")


# Global data manager instance
_data_manager = None


def get_data_manager() -> DataManager:
    """
    Get global DataManager instance (singleton pattern)
    
    Returns:
    --------
    manager : DataManager
    """
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager
