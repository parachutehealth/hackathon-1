#!/usr/bin/env python3
"""
Script to stop the running Streamlit application
"""

import subprocess
import sys

def stop_streamlit():
    """Stop the running Streamlit application"""
    try:
        # Find and kill streamlit processes
        result = subprocess.run(
            ["pkill", "-f", "streamlit"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Streamlit application stopped successfully")
        else:
            print("ℹ️  No running Streamlit applications found")
            
    except Exception as e:
        print(f"❌ Error stopping Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    stop_streamlit() 