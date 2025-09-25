#!/usr/bin/env python3
"""
Simple test for LLM matcher with minimal data.
"""

import os
from llm_matcher import LLMMatcher

def simple_test():
    """Test with just one supplier SKU and a few catalog SKUs."""
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Simple test data
    supplier_sku = {
        'Manufacturer ID': 'TEST-001',
        'Description': '3M Medipore H High Adhesion Soft Cloth Surgical Tape, 2 in. x 2 yd.',
        'Product Family': 'SILVER PRODUCTS',
        'Packaging': 'Case (12)',
        'HCPCS Code': 'A4452'
    }
    
    catalog_skus = [
        {
            'sku_external_id': '19-RCR5-V3GN-N1J',
            'sku_description': '3M Medipore H High Adhesion Soft Cloth Surgical Tape, 2 in. x 2 yd., Each (1)',
            'sku_hcpcs': 'A4452',
            'package_name': '3M Medipore H High Adhesion Soft Cloth Surgical Tape',
            'product_name': '3M Medipore H High Adhesion Soft Cloth Surgical Tape',
            'attributes': {'Brand': 'Medipore H', 'Dimensions': '2 in. x 2 yd.'}
        },
        {
            'sku_external_id': '5F-RVU6-N3KAN-TL',
            'sku_description': '3M Medipore H High Adhesion Soft Cloth Surgical Tape, 8 in. x 10 yd., Box (6)',
            'sku_hcpcs': 'A4452',
            'package_name': '3M Medipore H High Adhesion Soft Cloth Surgical Tape',
            'product_name': '3M Medipore H High Adhesion Soft Cloth Surgical Tape',
            'attributes': {'Brand': 'Medipore H', 'Dimensions': '8 in. x 10 yd.'}
        }
    ]
    
    print("Testing LLM matcher...")
    print(f"Supplier SKU: {supplier_sku['Description']}")
    print(f"Catalog SKUs: {len(catalog_skus)}")
    
    try:
        matcher = LLMMatcher(api_key, "gpt-3.5-turbo")
        results = matcher.match_single_sku(supplier_sku, catalog_skus)
        
        print(f"\nResults: {len(results)} matches found")
        for i, result in enumerate(results):
            print(f"\nMatch {i+1}:")
            print(f"  Catalog SKU: {result.matched_sku_id}")
            print(f"  Confidence: {result.confidence_score}%")
            print(f"  HCPCS Match: {result.hcpcs_match}")
            print(f"  Reasoning: {result.reasoning}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_test() 