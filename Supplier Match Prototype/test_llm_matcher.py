#!/usr/bin/env python3
"""
Test script for LLM matcher functionality.
"""

import sys
import os
from catalog_loader import load_catalog
from llm_matcher import LLMMatcher, prepare_catalog_for_matching, MatchResult


def test_llm_matcher():
    """Test the LLM matcher with sample data."""
    
    print("🤖 Testing LLM Matcher...")
    
    # Check if catalog file exists
    catalog_path = "parachute_catalog_woundcare.csv"
    if not os.path.exists(catalog_path):
        print(f"❌ Catalog file not found: {catalog_path}")
        return
    
    # Load catalog
    print("📦 Loading catalog...")
    packages = load_catalog(catalog_path)
    print(f"✅ Loaded {len(packages)} packages")
    
    # Prepare catalog for matching
    print("🔧 Preparing catalog for matching...")
    catalog_skus = prepare_catalog_for_matching(packages)
    print(f"✅ Prepared {len(catalog_skus)} catalog SKUs")
    
    # Sample supplier SKU for testing
    sample_supplier_sku = {
        'Manufacturer ID': 'TEST-001',
        'Description': '3M Medipore H High Adhesion Soft Cloth Surgical Tape, 2 in. x 2 yd.',
        'Product Family': 'SILVER PRODUCTS',
        'Packaging': 'Case (12)',
        'HCPCS Code': 'A4452'
    }
    
    print(f"\n📋 Sample supplier SKU:")
    print(f"   ID: {sample_supplier_sku['Manufacturer ID']}")
    print(f"   Description: {sample_supplier_sku['Description']}")
    print(f"   HCPCS: {sample_supplier_sku['HCPCS Code']}")
    
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n⚠️  No OpenAI API key found in environment.")
        print("   Set OPENAI_API_KEY environment variable to test LLM matching.")
        print("   Example: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Test LLM matcher
    print("\n🤖 Testing LLM matching...")
    try:
        matcher = LLMMatcher(api_key, "gpt-3.5-turbo")  # Use cheaper model for testing
        
        # Test with a small subset of catalog SKUs
        test_catalog_skus = catalog_skus[:10]  # First 10 SKUs for testing
        
        results = matcher.match_single_sku(sample_supplier_sku, test_catalog_skus)
        
        if results:
            print(f"✅ Found {len(results)} matches!")
            
            for i, result in enumerate(results[:3]):  # Show first 3 matches
                print(f"\n🎯 Match {i+1}:")
                print(f"   Catalog SKU: {result.matched_sku_id}")
                print(f"   Confidence: {result.confidence_score:.1f}%")
                print(f"   HCPCS Match: {'✅' if result.hcpcs_match else '❌'}")
                print(f"   Package: {result.package_name}")
                print(f"   Reasoning: {result.reasoning[:100]}...")
        else:
            print("❌ No matches found.")
            
    except Exception as e:
        print(f"❌ Error testing LLM matcher: {e}")
    
    print("\n✅ LLM matcher test complete!")


if __name__ == "__main__":
    test_llm_matcher() 