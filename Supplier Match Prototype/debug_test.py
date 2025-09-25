#!/usr/bin/env python3
"""
Debug script to test LLM matching with a single Drawtex SKU
"""

import os
import json
from llm_matcher import LLMMatcher, prepare_catalog_for_matching
from catalog_loader import load_catalog

def test_drawtex_matching():
    """Test matching a Drawtex supplier SKU"""
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Load catalog
    print("Loading catalog...")
    packages = load_catalog("parachute_catalog_woundcare.csv")
    catalog_skus = prepare_catalog_for_matching(packages)
    
    # Find Drawtex products in catalog
    drawtex_skus = [sku for sku in catalog_skus if 'drawtex' in sku['sku_description'].lower()]
    print(f"Found {len(drawtex_skus)} Drawtex products in catalog")
    
    # Show first few Drawtex products
    for i, sku in enumerate(drawtex_skus[:3]):
        print(f"{i+1}. {sku['sku_description']} (ID: {sku['sku_external_id']})")
    
    # Create a test supplier SKU
    supplier_sku = {
        'Manufacturer ID': 'TEST-DRAWTEX-001',
        'Description': 'Drawtex Hydroconductive Wound Dressing with LevaFiber, Box (10)',
        'Product Family': 'Wound Care',
        'Packaging': 'Box (10)',
        'HCPCS Code': 'A6199'
    }
    
    print(f"\nTesting supplier SKU: {supplier_sku['Description']}")
    
    # Test matching
    matcher = LLMMatcher(api_key, "gpt-4")
    
    print(f"\nTotal catalog SKUs available: {len(catalog_skus)}")
    print("First 5 catalog SKUs being sent to LLM:")
    for i, sku in enumerate(catalog_skus[:5]):
        print(f"{i+1}. {sku['sku_description']} (ID: {sku['sku_external_id']})")
    
    print("\nCalling LLM matcher...")
    results = matcher.match_single_sku(supplier_sku, catalog_skus)
    
    print(f"\nResults: {len(results)} matches found")
    for result in results:
        print(f"- {result.matched_sku_id}: {result.matched_description} (Confidence: {result.confidence_score}%)")
        print(f"  Reasoning: {result.reasoning}")

if __name__ == "__main__":
    test_drawtex_matching() 