"""
Catalog loader for Parachute wound care catalog data.

Loads flat CSV data into hierarchical Package -> Product -> SKU structure.
"""

import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SKU:
    """SKU (Stock Keeping Unit) with attributes."""
    external_id: str
    description: str
    hcpcs: str
    attrs: Dict[str, str]


@dataclass
class Product:
    """Product with required flag and associated SKUs."""
    external_id: str
    name: str
    required: bool
    skus: List[SKU]


@dataclass
class Package:
    """Package containing multiple products."""
    external_id: str
    name: str
    products: List[Product]


def _extract_attributes(row: pd.Series) -> Dict[str, str]:
    """Extract attribute name-value pairs from a CSV row."""
    attrs = {}
    
    # Look for attr1_name, attr1_value, attr2_name, attr2_value, etc.
    for i in range(1, 11):  # Support up to 10 attribute pairs
        name_col = f'attr{i}_name'
        value_col = f'attr{i}_value'
        
        if name_col in row and value_col in row:
            name = row[name_col]
            value = row[value_col]
            
            # Only add non-empty attributes
            if pd.notna(name) and pd.notna(value) and str(name).strip() and str(value).strip():
                attrs[str(name).strip()] = str(value).strip()
    
    return attrs


def load_catalog(path: str) -> Dict[str, Package]:
    """
    Load Parachute catalog from CSV file into hierarchical structure.
    
    Args:
        path: Path to the CSV file
        
    Returns:
        Dictionary of Package objects keyed by package external_id
    """
    # Read CSV file
    df = pd.read_csv(path)
    
    # Group by package
    packages = {}
    
    for package_id, package_group in df.groupby('package_external_id'):
        package_name = package_group['package_name'].iloc[0]
        products = {}
        
        # Group by product within package
        for product_id, product_group in package_group.groupby('product_external_id'):
            product_name = product_group['product_name'].iloc[0]
            product_required = str(product_group['product_required'].iloc[0]).upper() == 'TRUE'
            skus = []
            
            # Create SKUs for this product
            for _, sku_row in product_group.iterrows():
                sku = SKU(
                    external_id=sku_row['sku_external_id'],
                    description=sku_row['sku_description'],
                    hcpcs=sku_row['sku_hcpcs'] if pd.notna(sku_row['sku_hcpcs']) else '',
                    attrs=_extract_attributes(sku_row)
                )
                skus.append(sku)
            
            # Create Product
            product = Product(
                external_id=product_id,
                name=product_name,
                required=product_required,
                skus=skus
            )
            products[product_id] = product
        
        # Create Package
        package = Package(
            external_id=package_id,
            name=package_name,
            products=list(products.values())
        )
        packages[package_id] = package
    
    return packages


def main():
    """Test the catalog loader with sample data."""
    try:
        packages = load_catalog("parachute_catalog_woundcare.csv")
        print(f"📦 Loaded {len(packages)} packages")
        
        if packages:
            first_package = list(packages.values())[0]
            print(f"📋 First package: {first_package.name}")
            print(f"   Products: {len(first_package.products)}")
            
            if first_package.products:
                first_product = first_package.products[0]
                print(f"🔧 First product: {first_product.name}")
                print(f"   Required: {first_product.required}")
                print(f"   SKUs: {len(first_product.skus)}")
                
                if first_product.skus:
                    first_sku = first_product.skus[0]
                    print(f"🏷️  First SKU: {first_sku.external_id}")
                    print(f"   Description: {first_sku.description}")
                    print(f"   HCPCS: {first_sku.hcpcs}")
                    print(f"   Attributes: {len(first_sku.attrs)}")
        
        print("✅ Catalog loading successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 