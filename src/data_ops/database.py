"""
Database module for NexData - Enterprise-grade data storage
Provides SQLite backend for handling large datasets efficiently
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class DataStore:
    """
    Enterprise-grade data storage using SQLite
    Handles large datasets that don't fit in memory
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize data store
        
        Parameters:
        -----------
        db_path : str
            Path to SQLite database file (default: data/nexdata.db)
        """
        if db_path is None:
            # Create data directory if it doesn't exist
            data_dir = Path(__file__).parent.parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / 'nexdata.db'
        
        self.db_path = str(db_path)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection and create tables"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
            self.conn.execute("PRAGMA synchronous=NORMAL")  # Better performance
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def store_dataframe(self, df: pd.DataFrame, table_name: str, 
                       if_exists: str = 'replace') -> bool:
        """
        Store pandas DataFrame in database
        
        Parameters:
        -----------
        df : pd.DataFrame
            Data to store
        table_name : str
            Name of the table
        if_exists : str
            'replace', 'append', or 'fail'
        
        Returns:
        --------
        success : bool
        """
        try:
            df.to_sql(table_name, self.conn, if_exists=if_exists, index=False, 
                     chunksize=10000)  # Write in chunks for large data
            self.conn.commit()
            logger.info(f"Stored {len(df)} rows in table '{table_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to store dataframe: {e}")
            return False
    
    def load_dataframe(self, table_name: str, limit: Optional[int] = None,
                      offset: int = 0, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load DataFrame from database with pagination
        
        Parameters:
        -----------
        table_name : str
            Name of the table
        limit : int
            Number of rows to load (None = all)
        offset : int
            Starting row number
        columns : list
            Specific columns to load (None = all)
        
        Returns:
        --------
        df : pd.DataFrame
        """
        try:
            # Build query
            col_str = ', '.join(columns) if columns else '*'
            query = f"SELECT {col_str} FROM {table_name}"
            
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            df = pd.read_sql(query, self.conn)
            logger.info(f"Loaded {len(df)} rows from table '{table_name}'")
            return df
        except Exception as e:
            logger.error(f"Failed to load dataframe: {e}")
            return pd.DataFrame()
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute custom SQL query
        
        Parameters:
        -----------
        sql : str
            SQL query
        
        Returns:
        --------
        df : pd.DataFrame
        """
        try:
            df = pd.read_sql(sql, self.conn)
            return df
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return pd.DataFrame()
    
    def get_table_info(self, table_name: str) -> Tuple[int, List[str]]:
        """
        Get information about a table
        
        Parameters:
        -----------
        table_name : str
            Name of the table
        
        Returns:
        --------
        row_count : int
        columns : list
        """
        try:
            # Get row count
            cursor = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get column names
            cursor = self.conn.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            return row_count, columns
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return 0, []
    
    def list_tables(self) -> List[str]:
        """
        List all tables in database
        
        Returns:
        --------
        tables : list
        """
        try:
            cursor = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        try:
            cursor = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Failed to check table existence: {e}")
            return False
    
    def delete_table(self, table_name: str) -> bool:
        """
        Delete a table
        
        Parameters:
        -----------
        table_name : str
            Name of the table to delete
        
        Returns:
        --------
        success : bool
        """
        try:
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.commit()
            logger.info(f"Deleted table '{table_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete table: {e}")
            return False
    
    def create_index(self, table_name: str, column: str) -> bool:
        """
        Create index for faster queries
        
        Parameters:
        -----------
        table_name : str
            Name of the table
        column : str
            Column to index
        
        Returns:
        --------
        success : bool
        """
        try:
            index_name = f"idx_{table_name}_{column}"
            self.conn.execute(
                f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column})"
            )
            self.conn.commit()
            logger.info(f"Created index on {table_name}.{column}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Cleanup"""
        self.close()


# Global data store instance
_data_store = None


def get_data_store() -> DataStore:
    """
    Get global DataStore instance (singleton pattern)
    
    Returns:
    --------
    store : DataStore
    """
    global _data_store
    if _data_store is None:
        _data_store = DataStore()
    return _data_store
