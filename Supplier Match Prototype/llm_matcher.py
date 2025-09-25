"""
LLM-based SKU matching for supplier SKUs to Parachute catalog SKUs.
"""

import openai
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import time
import json


@dataclass
class MatchResult:
    """Result of a SKU matching operation."""
    supplier_sku_id: str
    supplier_description: str
    matched_sku_id: str
    matched_description: str
    confidence_score: float
    reasoning: str
    hcpcs_match: bool
    package_id: str
    package_name: str
    product_id: str
    product_name: str


class LLMMatcher:
    """LLM-based SKU matcher using OpenAI API."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the LLM matcher.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        openai.api_key = api_key
        self.client = openai
        self.model = model
    
    def _create_matching_prompt(self, supplier_sku: Dict, catalog_skus: List[Dict]) -> str:
        """
        Create a prompt for matching a supplier SKU to catalog SKUs.
        
        Args:
            supplier_sku: Supplier SKU data
            catalog_skus: List of catalog SKUs to match against
            
        Returns:
            Formatted prompt string
        """
        supplier_info = f"""
Supplier SKU to match:
- ID: {supplier_sku.get('Manufacturer ID', 'N/A')}
- Description: {supplier_sku.get('Description', 'N/A')}
- Product Family: {supplier_sku.get('Product Family', 'N/A')}
- Packaging: {supplier_sku.get('Packaging', 'N/A')}
- HCPCS Code: {supplier_sku.get('HCPCS Code', 'N/A')}
"""
        
        # Find relevant catalog SKUs (prioritize by brand match and HCPCS match)
        supplier_brand = supplier_sku.get('Product Family', '').lower()
        supplier_hcpcs = supplier_sku.get('HCPCS Code', '')
        
        # Sort catalog SKUs by relevance
        relevant_skus = []
        other_skus = []
        
        for sku in catalog_skus:
            sku_brand = sku.get('sku_description', '').lower()
            sku_hcpcs = sku.get('sku_hcpcs', '')
            
            # Check if this SKU is relevant
            brand_match = supplier_brand in sku_brand or any(word in sku_brand for word in supplier_brand.split())
            hcpcs_match = supplier_hcpcs == sku_hcpcs
            
            if brand_match or hcpcs_match:
                relevant_skus.append(sku)
            else:
                other_skus.append(sku)
        
        # Combine relevant SKUs first, then others, limit to 20 total
        prioritized_skus = relevant_skus + other_skus
        catalog_skus_to_show = prioritized_skus[:20]
        
        catalog_info = "Available catalog SKUs:\n"
        for i, sku in enumerate(catalog_skus_to_show):
            catalog_info += f"""
{i+1}. SKU ID: {sku.get('sku_external_id', 'N/A')}
   Description: {sku.get('sku_description', 'N/A')}
   HCPCS: {sku.get('sku_hcpcs', 'N/A')}
   Package: {sku.get('package_name', 'N/A')}
   Product: {sku.get('product_name', 'N/A')}
   Attributes: {sku.get('attributes', {})}
"""
        
        prompt = f"""
You are a medical supply matching expert. Your task is to find the best match for a supplier SKU from a list of catalog SKUs.

{supplier_info}

{catalog_info}

Please analyze the supplier SKU and find the best matching catalog SKU(s). Consider:
1. Product similarity (same type of medical supply)
2. HCPCS code matches (exact or similar)
3. Size/dimension compatibility
4. Brand/manufacturer alignment
5. Packaging similarities

IMPORTANT: You MUST respond with ONLY a valid JSON array. Do not include any explanatory text before or after the JSON.

If you find matches, return this exact JSON format:
[
  {{
    "catalog_sku_id": "string",
    "confidence_score": 95.5,
    "reasoning": "string",
    "hcpcs_match": true
  }}
]

If you find NO matches, return an empty array:
[]

Only include matches with confidence >= 70%. Sort by confidence descending.
"""
        
        return prompt
    
    def match_single_sku(self, supplier_sku: Dict, catalog_skus: List[Dict]) -> List[MatchResult]:
        """
        Match a single supplier SKU to catalog SKUs using LLM.
        
        Args:
            supplier_sku: Supplier SKU data
            catalog_skus: List of catalog SKUs to match against
            
        Returns:
            List of MatchResult objects
        """
        try:
            prompt = self._create_matching_prompt(supplier_sku, catalog_skus)
            
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical supply matching expert. Provide accurate, detailed matching analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Debug: Print the raw response
            print(f"Raw LLM response for SKU {supplier_sku.get('Manufacturer ID', 'Unknown')}:")
            print(f"Content: {content}")
            print("---")
            
            # Handle empty or invalid responses
            if not content or content == "":
                print(f"Empty response for SKU {supplier_sku.get('Manufacturer ID', 'Unknown')}")
                return []
            
            try:
                matches = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"JSON decode error for SKU {supplier_sku.get('Manufacturer ID', 'Unknown')}: {e}")
                print(f"Response content: {content[:200]}...")
                
                # Try to extract JSON from the response if it contains explanatory text
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    try:
                        matches = json.loads(json_match.group())
                        print(f"Successfully extracted JSON from response")
                    except:
                        print(f"Failed to extract valid JSON from response")
                        return []
                else:
                    return []
            
            # Convert to MatchResult objects
            results = []
            for match in matches:
                # Find the catalog SKU details
                catalog_sku = next(
                    (sku for sku in catalog_skus if sku.get('sku_external_id') == match['catalog_sku_id']), 
                    None
                )
                
                if catalog_sku:
                    result = MatchResult(
                        supplier_sku_id=supplier_sku.get('Manufacturer ID', ''),
                        supplier_description=supplier_sku.get('Description', ''),
                        matched_sku_id=match['catalog_sku_id'],
                        matched_description=catalog_sku.get('sku_description', ''),
                        confidence_score=match['confidence_score'],
                        reasoning=match['reasoning'],
                        hcpcs_match=match['hcpcs_match'],
                        package_id=catalog_sku.get('package_external_id', ''),
                        package_name=catalog_sku.get('package_name', ''),
                        product_id=catalog_sku.get('product_external_id', ''),
                        product_name=catalog_sku.get('product_name', '')
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower():
                print(f"Rate limit hit for SKU {supplier_sku.get('Manufacturer ID', 'Unknown')}. Waiting 60 seconds...")
                time.sleep(60)  # Wait 60 seconds for rate limit to reset
                return []  # Skip this SKU for now
            else:
                print(f"Error matching SKU {supplier_sku.get('Manufacturer ID', 'Unknown')}: {e}")
            return []
    
    def match_supplier_skus(self, supplier_skus: List[Dict], catalog_skus: List[Dict], 
                           batch_size: int = 5) -> List[MatchResult]:
        """
        Match multiple supplier SKUs to catalog SKUs in batches.
        
        Args:
            supplier_skus: List of supplier SKU data
            catalog_skus: List of catalog SKUs to match against
            batch_size: Number of SKUs to process in each batch
            
        Returns:
            List of MatchResult objects
        """
        all_results = []
        
        # Process in batches
        for i in range(0, len(supplier_skus), batch_size):
            batch = supplier_skus[i:i + batch_size]
            
            for supplier_sku in batch:
                results = self.match_single_sku(supplier_sku, catalog_skus)
                all_results.extend(results)
                
                # Rate limiting delay
                time.sleep(1.0)  # Increased delay to avoid rate limits
        
        return all_results


def prepare_catalog_for_matching(packages: Dict) -> List[Dict]:
    """
    Prepare catalog data for LLM matching.
    
    Args:
        packages: Dictionary of Package objects from catalog_loader
        
    Returns:
        List of catalog SKU dictionaries
    """
    catalog_skus = []
    
    for package in packages.values():
        for product in package.products:
            for sku in product.skus:
                catalog_sku = {
                    'sku_external_id': sku.external_id,
                    'sku_description': sku.description,
                    'sku_hcpcs': sku.hcpcs,
                    'package_external_id': package.external_id,
                    'package_name': package.name,
                    'product_external_id': product.external_id,
                    'product_name': product.name,
                    'attributes': sku.attrs
                }
                catalog_skus.append(catalog_sku)
    
    return catalog_skus


def test_matcher():
    """Test the LLM matcher with sample data."""
    # This would be used for testing without the full app
    print("LLM Matcher module loaded successfully!")
    print("Use this module with OpenAI API key for SKU matching.")


if __name__ == "__main__":
    test_matcher() 