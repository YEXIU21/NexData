"""
Performance Monitoring
Monitor application performance and resource usage

SEPARATION OF CONCERNS: Performance monitoring only
"""

import time
import psutil
import os
from datetime import datetime


class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.operation_times = {}
    
    def start_operation(self, operation_name):
        """Start timing an operation"""
        self.operation_times[operation_name] = {'start': time.time()}
    
    def end_operation(self, operation_name):
        """End timing an operation"""
        if operation_name in self.operation_times:
            elapsed = time.time() - self.operation_times[operation_name]['start']
            self.operation_times[operation_name]['duration'] = elapsed
            return elapsed
        return None
    
    @staticmethod
    def get_memory_usage():
        """
        Get current memory usage
        
        Returns:
        --------
        memory_info : dict
            Memory usage information
        """
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent()
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_cpu_usage():
        """
        Get CPU usage
        
        Returns:
        --------
        cpu_info : dict
            CPU usage information
        """
        try:
            process = psutil.Process(os.getpid())
            
            return {
                'percent': process.cpu_percent(interval=0.1),
                'num_threads': process.num_threads(),
                'system_wide': psutil.cpu_percent(interval=0.1)
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_system_info():
        """
        Get system information
        
        Returns:
        --------
        system_info : dict
            System information
        """
        try:
            virtual_mem = psutil.virtual_memory()
            
            return {
                'total_memory_gb': virtual_mem.total / 1024 / 1024 / 1024,
                'available_memory_gb': virtual_mem.available / 1024 / 1024 / 1024,
                'memory_percent': virtual_mem.percent,
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=0.1)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_performance_report(self):
        """
        Generate performance report
        
        Returns:
        --------
        report : dict
            Performance metrics
        """
        uptime = time.time() - self.start_time
        
        report = {
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_duration(uptime),
            'memory': self.get_memory_usage(),
            'cpu': self.get_cpu_usage(),
            'system': self.get_system_info(),
            'operations': {}
        }
        
        # Add operation times
        for op_name, op_data in self.operation_times.items():
            if 'duration' in op_data:
                report['operations'][op_name] = {
                    'duration_seconds': op_data['duration'],
                    'duration_formatted': self._format_duration(op_data['duration'])
                }
        
        return report
    
    @staticmethod
    def _format_duration(seconds):
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.2f}h"
    
    @staticmethod
    def format_performance_report(report):
        """
        Format performance report as text
        
        Parameters:
        -----------
        report : dict
            Performance report
        
        Returns:
        --------
        formatted : str
            Formatted report text
        """
        text = f"\n{'='*60}\n"
        text += "PERFORMANCE MONITORING REPORT\n"
        text += f"{'='*60}\n\n"
        
        text += f"Application Uptime: {report['uptime_formatted']}\n\n"
        
        text += "--- MEMORY USAGE ---\n"
        if 'error' not in report['memory']:
            text += f"Process Memory: {report['memory']['rss_mb']:.2f} MB\n"
            text += f"Memory Percent: {report['memory']['percent']:.2f}%\n\n"
        
        text += "--- CPU USAGE ---\n"
        if 'error' not in report['cpu']:
            text += f"Process CPU: {report['cpu']['percent']:.2f}%\n"
            text += f"Threads: {report['cpu']['num_threads']}\n"
            text += f"System CPU: {report['cpu']['system_wide']:.2f}%\n\n"
        
        text += "--- SYSTEM INFO ---\n"
        if 'error' not in report['system']:
            text += f"Total Memory: {report['system']['total_memory_gb']:.2f} GB\n"
            text += f"Available Memory: {report['system']['available_memory_gb']:.2f} GB\n"
            text += f"CPU Cores: {report['system']['cpu_count']}\n\n"
        
        if report['operations']:
            text += "--- OPERATION TIMES ---\n"
            sorted_ops = sorted(report['operations'].items(), 
                              key=lambda x: x[1]['duration_seconds'], 
                              reverse=True)
            for op_name, op_data in sorted_ops:
                text += f"{op_name}: {op_data['duration_formatted']}\n"
        
        text += f"\n{'='*60}\n"
        
        return text
    
    @staticmethod
    def get_optimization_tips(report):
        """
        Generate optimization tips based on performance metrics
        
        Parameters:
        -----------
        report : dict
            Performance report
        
        Returns:
        --------
        tips : list
            Optimization suggestions
        """
        tips = []
        
        # Memory tips
        if 'error' not in report['memory']:
            if report['memory']['percent'] > 50:
                tips.append("⚠️ High memory usage detected. Consider processing data in chunks.")
            if report['memory']['rss_mb'] > 1000:
                tips.append("💡 Memory usage exceeds 1GB. Optimize data types or filter unnecessary columns.")
        
        # CPU tips
        if 'error' not in report['cpu']:
            if report['cpu']['percent'] > 80:
                tips.append("⚠️ High CPU usage. Consider optimizing calculations or using vectorized operations.")
        
        # System tips
        if 'error' not in report['system']:
            if report['system']['memory_percent'] > 90:
                tips.append("⚠️ System memory critically low. Close other applications.")
        
        # Operation tips
        if report['operations']:
            slow_ops = {k: v for k, v in report['operations'].items() 
                       if v['duration_seconds'] > 5}
            if slow_ops:
                tips.append(f"⚠️ {len(slow_ops)} operations took >5 seconds. Review for optimization.")
        
        if not tips:
            tips.append("✓ Performance is optimal")
        
        return tips
