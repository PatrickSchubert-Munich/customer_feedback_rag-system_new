"""
🗑️ Chart Cleanup Utility - Automatic Chart File Management

Provides functionality to automatically delete old chart files
to save disk space and maintain a clean charts directory.
"""

import os
import time
from typing import Tuple


def cleanup_old_charts(max_age_minutes: int = 60, charts_dir: str = "charts") -> Tuple[int, int]:
    """
    Deletes chart files older than specified age.
    
    Args:
        max_age_minutes (int): Maximum age of chart files in minutes. 
                               Files older than this will be deleted. Defaults to 60.
        charts_dir (str): Directory containing chart files. Defaults to "charts".
        
    Returns:
        Tuple[int, int]: Tuple containing:
            - deleted_count (int): Number of files successfully deleted
            - total_checked (int): Total number of files checked
            
    Features:
        - Only deletes .png files
        - Checks file modification time
        - Handles errors gracefully (continues on individual file errors)
        - Returns statistics for logging/display
        
    Example:
        >>> deleted, total = cleanup_old_charts(max_age_minutes=60)
        >>> print(f"Deleted {deleted} of {total} charts")
    """
    if not os.path.exists(charts_dir):
        return 0, 0
    
    current_time = time.time()
    max_age_seconds = max_age_minutes * 60
    
    deleted_count = 0
    total_checked = 0
    
    try:
        # Get all .png files in charts directory
        chart_files = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
        total_checked = len(chart_files)
        
        for filename in chart_files:
            file_path = os.path.join(charts_dir, filename)
            
            try:
                # Get file modification time
                file_mtime = os.path.getmtime(file_path)
                file_age_seconds = current_time - file_mtime
                
                # Delete if older than max_age
                if file_age_seconds > max_age_seconds:
                    os.remove(file_path)
                    deleted_count += 1
                    
            except Exception as e:
                # Continue with other files if one fails
                print(f"⚠️ Error deleting {filename}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error accessing charts directory: {e}")
        return 0, 0
    
    return deleted_count, total_checked


def get_chart_statistics(charts_dir: str = "charts") -> dict:
    """
    Gets statistics about chart files in directory.
    
    Args:
        charts_dir (str): Directory containing chart files. Defaults to "charts".
        
    Returns:
        dict: Dictionary containing statistics with keys:
            - total_files (int): Total number of chart files
            - total_size_mb (float): Total size in megabytes
            - oldest_age_minutes (float): Age of oldest file in minutes
            - newest_age_minutes (float): Age of newest file in minutes
            
    Features:
        - Only counts .png files
        - Returns 0 values if directory doesn't exist
        - Calculates file ages based on modification time
        
    Example:
        >>> stats = get_chart_statistics()
        >>> print(f"Total charts: {stats['total_files']}, Size: {stats['total_size_mb']:.2f} MB")
    """
    if not os.path.exists(charts_dir):
        return {
            'total_files': 0,
            'total_size_mb': 0.0,
            'oldest_age_minutes': 0.0,
            'newest_age_minutes': 0.0
        }
    
    current_time = time.time()
    chart_files = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
    
    if not chart_files:
        return {
            'total_files': 0,
            'total_size_mb': 0.0,
            'oldest_age_minutes': 0.0,
            'newest_age_minutes': 0.0
        }
    
    total_size = 0
    ages = []
    
    for filename in chart_files:
        file_path = os.path.join(charts_dir, filename)
        try:
            # Get file size
            total_size += os.path.getsize(file_path)
            
            # Get file age
            file_mtime = os.path.getmtime(file_path)
            age_minutes = (current_time - file_mtime) / 60
            ages.append(age_minutes)
        except Exception:
            continue
    
    return {
        'total_files': len(chart_files),
        'total_size_mb': total_size / (1024 * 1024),
        'oldest_age_minutes': max(ages) if ages else 0.0,
        'newest_age_minutes': min(ages) if ages else 0.0
    }


def cleanup_charts_if_enabled(max_age_minutes: int = 60) -> Tuple[int, int]:
    """
    Cleanup wrapper that checks session state before executing.
    
    This function is designed to be called from Streamlit apps
    and respects the 'auto_delete_charts' session state setting.
    
    Args:
        max_age_minutes (int): Maximum age of chart files in minutes. Defaults to 60.
        
    Returns:
        Tuple[int, int]: Tuple containing (deleted_count, total_checked)
                        Returns (0, 0) if auto-delete is disabled.
                        
    Notes:
        - Only executes if st.session_state.auto_delete_charts is True
        - Safe to call even if Streamlit is not available
        - Returns (0, 0) without error if session state not found
        
    Example:
        >>> # In Streamlit app
        >>> if st.session_state.get('auto_delete_charts', False):
        >>>     deleted, total = cleanup_charts_if_enabled()
        >>>     st.caption(f"🗑️ Deleted {deleted}/{total} old charts")
    """
    try:
        import streamlit as st
        if not st.session_state.get('auto_delete_charts', False):
            return 0, 0
    except (ImportError, AttributeError):
        # Streamlit not available or session_state not initialized
        return 0, 0
    
    return cleanup_old_charts(max_age_minutes=max_age_minutes)
