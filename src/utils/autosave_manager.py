"""
AutoSave Manager - Automatic data backup and crash recovery
Saves work periodically and provides crash recovery functionality
"""

import os
import pandas as pd
from datetime import datetime
import json
import threading
import time


class AutoSaveManager:
    """
    Manages automatic saving and crash recovery for NexData
    """
    
    def __init__(self, save_interval=300):  # 5 minutes default
        """
        Initialize AutoSave Manager
        
        Parameters:
        -----------
        save_interval : int
            Seconds between auto-saves (default: 300 = 5 minutes)
        """
        self.save_interval = save_interval
        self.autosave_dir = os.path.join(os.path.dirname(__file__), '..', '..', '.autosave')
        self.is_running = False
        self.thread = None
        self.current_df = None
        self.original_path = None
        self.last_save_time = None
        
        # Create autosave directory if not exists
        os.makedirs(self.autosave_dir, exist_ok=True)
        
        # Load metadata
        self.metadata_path = os.path.join(self.autosave_dir, 'metadata.json')
        self.metadata = self._load_metadata()
    
    def _load_metadata(self):
        """Load autosave metadata"""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save autosave metadata"""
        try:
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def start(self, df, original_path=None):
        """
        Start auto-save thread
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame to auto-save
        original_path : str
            Original file path (optional)
        """
        if self.is_running:
            self.stop()
        
        self.current_df = df
        self.original_path = original_path
        self.is_running = True
        
        # Start background thread
        self.thread = threading.Thread(target=self._autosave_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop auto-save thread"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.thread = None
    
    def update_data(self, df):
        """Update dataframe to be saved"""
        self.current_df = df
    
    def _autosave_loop(self):
        """Background loop for auto-saving"""
        while self.is_running:
            time.sleep(self.save_interval)
            
            if self.current_df is not None and self.is_running:
                try:
                    self._perform_autosave()
                except Exception as e:
                    print(f"AutoSave error: {e}")
    
    def _perform_autosave(self):
        """Perform the actual auto-save"""
        if self.current_df is None:
            return
        
        # Generate autosave filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        autosave_file = os.path.join(self.autosave_dir, f"autosave_{timestamp}.csv")
        
        # Save dataframe
        self.current_df.to_csv(autosave_file, index=False)
        
        # Update metadata
        self.metadata = {
            'last_autosave': autosave_file,
            'timestamp': timestamp,
            'original_path': self.original_path,
            'rows': len(self.current_df),
            'columns': len(self.current_df.columns)
        }
        self._save_metadata()
        
        self.last_save_time = datetime.now()
        
        # Clean up old autosaves (keep only last 5)
        self._cleanup_old_autosaves()
    
    def _cleanup_old_autosaves(self):
        """Remove old autosave files, keep only last 5"""
        try:
            autosaves = [f for f in os.listdir(self.autosave_dir) 
                        if f.startswith('autosave_') and f.endswith('.csv')]
            autosaves.sort(reverse=True)
            
            # Keep only 5 most recent
            for old_file in autosaves[5:]:
                os.remove(os.path.join(self.autosave_dir, old_file))
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def manual_save(self):
        """Manually trigger an auto-save"""
        if self.current_df is not None:
            self._perform_autosave()
            return True
        return False
    
    def has_recovery_data(self):
        """Check if there's recovery data available"""
        return os.path.exists(self.metadata_path) and 'last_autosave' in self.metadata
    
    def get_recovery_info(self):
        """
        Get information about available recovery data
        
        Returns:
        --------
        dict or None
            Recovery information or None if no recovery data
        """
        if not self.has_recovery_data():
            return None
        
        autosave_file = self.metadata.get('last_autosave')
        if not os.path.exists(autosave_file):
            return None
        
        return {
            'file': autosave_file,
            'timestamp': self.metadata.get('timestamp'),
            'original_path': self.metadata.get('original_path'),
            'rows': self.metadata.get('rows'),
            'columns': self.metadata.get('columns'),
            'size_mb': os.path.getsize(autosave_file) / (1024 * 1024)
        }
    
    def recover_data(self):
        """
        Recover data from autosave
        
        Returns:
        --------
        pd.DataFrame or None
            Recovered dataframe or None if recovery failed
        """
        recovery_info = self.get_recovery_info()
        if not recovery_info:
            return None
        
        try:
            df = pd.read_csv(recovery_info['file'])
            return df
        except Exception as e:
            print(f"Recovery error: {e}")
            return None
    
    def clear_recovery_data(self):
        """Clear all recovery data and autosaves"""
        try:
            # Remove all autosave files
            for f in os.listdir(self.autosave_dir):
                if f.startswith('autosave_') or f == 'metadata.json':
                    os.remove(os.path.join(self.autosave_dir, f))
            
            self.metadata = {}
            return True
        except Exception as e:
            print(f"Clear error: {e}")
            return False
    
    def get_last_save_time(self):
        """Get timestamp of last save"""
        return self.last_save_time
    
    def get_save_status(self):
        """
        Get current save status
        
        Returns:
        --------
        str
            Status message
        """
        if not self.is_running:
            return "Auto-save: OFF"
        
        if self.last_save_time:
            elapsed = (datetime.now() - self.last_save_time).seconds
            minutes_ago = elapsed // 60
            if minutes_ago == 0:
                return "Auto-save: Just saved"
            else:
                return f"Auto-save: {minutes_ago}m ago"
        
        return "Auto-save: Waiting for first save"


# Global instance
_autosave_manager = None

def get_autosave_manager(save_interval=300):
    """Get global AutoSave Manager instance"""
    global _autosave_manager
    if _autosave_manager is None:
        _autosave_manager = AutoSaveManager(save_interval)
    return _autosave_manager
