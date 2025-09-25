#!/usr/bin/env python3
"""
Test script to verify CSV validation logic
"""

import pandas as pd
import sys
import os

# Required columns as specified in the plan
REQUIRED_COLUMNS = [
    "Product Family",
    "Manufacturer ID", 
    "Description",
    "Packaging",
    "HCPCS Code"
]

def validate_csv_columns(df):
    """
    Validate that the uploaded CSV contains exactly the required 5 columns.
    
    Args:
        df: pandas DataFrame from uploaded CSV
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "No data found in the uploaded file."
    
    # Check if all required columns are present
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    extra_columns = set(df.columns) - set(REQUIRED_COLUMNS)
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    if extra_columns:
        return False, f"Unexpected columns found: {', '.join(extra_columns)}"
    
    return True, "CSV validation successful!"

def main():
    # Test with the corrected testskus_corrected.csv file
    test_file = "testskus_corrected.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found!")
        sys.exit(1)
    
    print(f"📊 Testing CSV validation with {test_file}")
    print("=" * 50)
    
    try:
        # Read the CSV file
        df = pd.read_csv(test_file)
        
        print(f"📋 Found columns: {list(df.columns)}")
        print(f"📊 Total rows: {len(df)}")
        print(f"📊 Total columns: {len(df.columns)}")
        
        # Validate the columns
        is_valid, message = validate_csv_columns(df)
        
        if is_valid:
            print(f"✅ {message}")
            print("\n👀 First 5 rows:")
            print(df.head().to_string(index=False))
        else:
            print(f"❌ {message}")
            print(f"\n🔍 Expected columns: {REQUIRED_COLUMNS}")
            print(f"🔍 Actual columns: {list(df.columns)}")
            
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 