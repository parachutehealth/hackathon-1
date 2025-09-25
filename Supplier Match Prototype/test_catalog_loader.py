#!/usr/bin/env python3
"""
Test script for catalog_loader.py
"""

import sys
import os
from catalog_loader import load_catalog, Package, Product, SKU


def test_catalog_loader():
    """Test the catalog loader functionality."""
    
    # Test file path
    catalog_path = "parachute_catalog_woundcare.csv"
    
    # Check if file exists
    assert os.path.exists(catalog_path), f"Catalog file not found: {catalog_path}"
    
    # Load catalog
    packages = load_catalog(catalog_path)
    
    # Basic assertions
    assert isinstance(packages, dict), "packages should be a dictionary"
    assert len(packages) > 0, "Should load at least one package"
    
    print(f"✅ Loaded {len(packages)} packages")
    
    # Get first package for detailed testing
    first_package_id = list(packages.keys())[0]
    first_package = packages[first_package_id]
    
    # Test Package structure
    assert isinstance(first_package, Package), "First item should be a Package"
    assert hasattr(first_package, 'external_id'), "Package should have external_id"
    assert hasattr(first_package, 'name'), "Package should have name"
    assert hasattr(first_package, 'products'), "Package should have products"
    assert isinstance(first_package.products, list), "Package.products should be a list"
    
    print(f"✅ First package: {first_package.name} ({first_package.external_id})")
    print(f"   Products: {len(first_package.products)}")
    
    # Test Product structure
    if first_package.products:
        first_product = first_package.products[0]
        
        assert isinstance(first_product, Product), "First product should be a Product"
        assert hasattr(first_product, 'external_id'), "Product should have external_id"
        assert hasattr(first_product, 'name'), "Product should have name"
        assert hasattr(first_product, 'required'), "Product should have required"
        assert hasattr(first_product, 'skus'), "Product should have skus"
        assert isinstance(first_product.skus, list), "Product.skus should be a list"
        assert isinstance(first_product.required, bool), "Product.required should be a boolean"
        
        print(f"✅ First product: {first_product.name} ({first_product.external_id})")
        print(f"   Required: {first_product.required}")
        print(f"   SKUs: {len(first_product.skus)}")
        
        # Test SKU structure
        if first_product.skus:
            first_sku = first_product.skus[0]
            
            assert isinstance(first_sku, SKU), "First SKU should be a SKU"
            assert hasattr(first_sku, 'external_id'), "SKU should have external_id"
            assert hasattr(first_sku, 'description'), "SKU should have description"
            assert hasattr(first_sku, 'hcpcs'), "SKU should have hcpcs"
            assert hasattr(first_sku, 'attrs'), "SKU should have attrs"
            assert isinstance(first_sku.attrs, dict), "SKU.attrs should be a dictionary"
            
            print(f"✅ First SKU: {first_sku.external_id}")
            print(f"   Description: {first_sku.description}")
            print(f"   HCPCS: {first_sku.hcpcs}")
            print(f"   Attributes: {len(first_sku.attrs)}")
            
            if first_sku.attrs:
                sample_attr = list(first_sku.attrs.items())[0]
                print(f"   Sample attr: {sample_attr}")
    
    # Test data integrity
    total_products = sum(len(pkg.products) for pkg in packages.values())
    total_skus = sum(len(prod.skus) for pkg in packages.values() for prod in pkg.products)
    
    print(f"\n📊 Summary:")
    print(f"   Total packages: {len(packages)}")
    print(f"   Total products: {total_products}")
    print(f"   Total SKUs: {total_skus}")
    
    # Verify we have reasonable numbers
    assert total_products > 0, "Should have at least one product"
    assert total_skus > 0, "Should have at least one SKU"
    
    print(f"\n🎉 All tests passed!")


def main():
    """Run the test suite."""
    try:
        test_catalog_loader()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 