import streamlit as st
import pandas as pd
from io import StringIO
from catalog_loader import load_catalog, Package, Product, SKU
from llm_matcher import LLMMatcher, prepare_catalog_for_matching, MatchResult

# Page configuration
st.set_page_config(
    page_title="Supplier Match Prototype",
    page_icon="📊",
    layout="wide"
)

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

def display_catalog_info(packages):
    """Display catalog information in a nice format."""
    if not packages:
        st.warning("No catalog data loaded.")
        return
    
    st.subheader("📦 Catalog Information")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Packages", len(packages))
    
    total_products = sum(len(pkg.products) for pkg in packages.values())
    with col2:
        st.metric("Total Products", total_products)
    
    total_skus = sum(len(prod.skus) for pkg in packages.values() for prod in pkg.products)
    with col3:
        st.metric("Total SKUs", total_skus)
    
    # Package details
    st.subheader("📋 Package Details")
    
    # Create a searchable selectbox for package selection
    package_ids = list(packages.keys())
    package_options = [f"{packages[x].name} ({x})" for x in package_ids]
    
    # Add search functionality
    package_search = st.text_input("🔍 Search packages:", placeholder="Type to search packages...")
    
    if package_search:
        # Filter packages based on search
        filtered_packages = []
        for pkg_id, pkg in packages.items():
            if (package_search.lower() in pkg.name.lower() or 
                package_search.lower() in pkg.external_id.lower()):
                filtered_packages.append(pkg_id)
    else:
        filtered_packages = package_ids
    
    if filtered_packages:
        selected_package_option = st.selectbox(
            "Select a package to view details:",
            filtered_packages,
            format_func=lambda x: f"{packages[x].name} ({x})"
        )
        selected_package_id = selected_package_option
    else:
        st.warning("No packages match your search.")
        selected_package_id = None
    
    if selected_package_id:
        package = packages[selected_package_id]
        
        st.write(f"**Package:** {package.name}")
        st.write(f"**ID:** {package.external_id}")
        st.write(f"**Products:** {len(package.products)}")
        
        # Show products with search
        st.subheader("🔧 Products")
        
        # Add product search
        product_search = st.text_input("🔍 Search products:", placeholder="Type to search products in this package...")
        
        if product_search:
            # Filter products based on search
            filtered_products = []
            for product in package.products:
                if (product_search.lower() in product.name.lower() or 
                    product_search.lower() in product.external_id.lower()):
                    filtered_products.append(product)
        else:
            filtered_products = package.products
        
        if filtered_products:
            for i, product in enumerate(filtered_products):
                with st.expander(f"{product.name} ({product.external_id})"):
                    st.write(f"**Required:** {product.required}")
                    st.write(f"**SKUs:** {len(product.skus)}")
                    
                    # Show first few SKUs
                    if product.skus:
                        st.write("**Sample SKUs:**")
                        for j, sku in enumerate(product.skus[:3]):  # Show first 3 SKUs
                            st.write(f"- {sku.external_id}: {sku.description}")
                            if sku.hcpcs:
                                st.write(f"  HCPCS: {sku.hcpcs}")
                            if sku.attrs:
                                st.write("  Attributes:")
                                for k, v in sku.attrs.items():
                                    st.write(f"    - {k}: {v}")
                            else:
                                st.write("  Attributes: None")
                        if len(product.skus) > 3:
                            st.write(f"... and {len(product.skus) - 3} more SKUs")
        else:
            st.warning("No products match your search.")

def main():
    st.title("📊 Supplier Match Prototype")
    st.markdown("Upload supplier SKUs and Parachute catalog data for matching.")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Supplier SKUs", "📦 Parachute Catalog", "🤖 LLM Matching", "🔍 Data Overview"])
    
    with tab1:
        st.header("📤 Supplier SKU Upload")
        st.markdown("Upload a CSV file with supplier SKU data for validation and preview.")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a supplier CSV file",
            type=['csv'],
            help="Upload a CSV file with exactly these columns: Product Family, Manufacturer ID, Description, Packaging, HCPCS Code"
        )
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                
                # Validate the columns
                is_valid, message = validate_csv_columns(df)
                
                if is_valid:
                    st.success("✅ " + message)
                    
                    # Display file info
                    st.subheader("📋 File Information")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Rows", len(df))
                    with col2:
                        st.metric("Total Columns", len(df.columns))
                    with col3:
                        st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
                    
                    # Display the first 5 rows
                    st.subheader("👀 Preview (First 5 Rows)")
                    st.dataframe(
                        df.head(),
                        use_container_width=True,
                        hide_index=False
                    )
                    
                    # Show column data types
                    st.subheader("📝 Column Information")
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Data Type': df.dtypes.astype(str),
                        'Non-Null Count': df.count(),
                        'Null Count': df.isnull().sum()
                    })
                    st.dataframe(col_info, use_container_width=True, hide_index=True)
                    
                else:
                    st.error("❌ " + message)
                    
                    # Show what columns were found
                    st.subheader("🔍 Found Columns")
                    st.write(f"**Expected columns:** {', '.join(REQUIRED_COLUMNS)}")
                    st.write(f"**Actual columns:** {', '.join(df.columns.tolist())}")
                    
            except Exception as e:
                st.error(f"❌ Error reading CSV file: {str(e)}")
        
        else:
            st.info("👆 Please upload a CSV file to begin validation.")
            
            # Show expected format
            st.subheader("📋 Expected CSV Format")
            st.markdown("""
            Your CSV file must contain exactly these 5 columns:
            
            | Column | Description |
            |--------|-------------|
            | Product Family | Product category or family name |
            | Manufacturer ID | Unique identifier from manufacturer |
            | Description | Product description |
            | Packaging | Packaging information |
            | HCPCS Code | Healthcare Common Procedure Coding System code |
            """)
    
    with tab2:
        st.header("📦 Parachute Catalog")
        st.markdown("Upload and explore the Parachute catalog data.")
        
        # Require user to upload a catalog file
        catalog_file = st.file_uploader(
            "Upload Parachute catalog CSV",
            type=['csv'],
            help="Upload the Parachute catalog CSV file"
        )
        
        if catalog_file is not None:
            try:
                # Save uploaded file temporarily
                with open("temp_catalog.csv", "wb") as f:
                    f.write(catalog_file.getbuffer())
                
                packages = load_catalog("temp_catalog.csv")
                display_catalog_info(packages)
                
                # Store in session state
                st.session_state.packages = packages
                
            except Exception as e:
                st.error(f"❌ Error loading catalog: {str(e)}")
        else:
            st.info("Please upload a Parachute catalog CSV to explore the catalog.")
    
    with tab3:
        st.header("🤖 LLM Matching")
        st.markdown("Match supplier SKUs to Parachute catalog SKUs using AI.")
        
        # Test mode option
        test_mode = st.checkbox("🧪 Test Mode (process only first 5 SKUs)", value=True, help="Enable to test with a small subset of SKUs")
        
        # Check if catalog is loaded
        if 'packages' not in st.session_state:
            st.warning("⚠️ Please load catalog data in the 'Parachute Catalog' tab first.")
            st.stop()
        
        # Use stored API key
        api_key = "REMOVED BY LINDA"
        
        # Supplier SKU upload
        st.subheader("📤 Upload Supplier SKUs")
        supplier_file = st.file_uploader(
            "Choose supplier CSV file",
            type=['csv'],
            key="supplier_llm"
        )
        
        if supplier_file is not None:
            try:
                supplier_df = pd.read_csv(supplier_file)
                
                # Validate supplier CSV
                is_valid, message = validate_csv_columns(supplier_df)
                
                if not is_valid:
                    st.error(f"❌ {message}")
                    st.stop()
                
                st.success(f"✅ {len(supplier_df)} supplier SKUs loaded")
                
                # Show supplier SKUs
                with st.expander("📋 Supplier SKUs Preview"):
                    st.dataframe(supplier_df.head(10), use_container_width=True)
                
                # Matching controls
                st.subheader("🎯 Matching Configuration")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    batch_size = st.selectbox("Batch Size", [1, 2, 3], index=0)
                
                with col2:
                    confidence_threshold = st.slider("Confidence Threshold (%)", 70, 100, 90)
                
                with col3:
                    model = st.selectbox("LLM Model", ["gpt-4", "gpt-3.5-turbo"], index=0)
                
                # Start matching button
                if st.button("🚀 Start LLM Matching", type="primary"):
                    with st.spinner("🤖 Processing SKUs with LLM..."):
                        try:
                            # Initialize matcher
                            matcher = LLMMatcher(api_key, model)
                            
                            # Prepare catalog data
                            catalog_skus = prepare_catalog_for_matching(st.session_state.packages)
                            
                            # Convert supplier data to list of dicts
                            supplier_skus = supplier_df.to_dict('records')
                            
                            # Apply test mode if enabled
                            if test_mode:
                                supplier_skus = supplier_skus[:5]  # Only process first 5 SKUs
                                st.info(f"🧪 Test mode enabled - processing only {len(supplier_skus)} SKUs")
                            
                            # Progress tracking
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Process in batches
                            all_results = []
                            total_batches = (len(supplier_skus) + batch_size - 1) // batch_size
                            
                            for i in range(0, len(supplier_skus), batch_size):
                                batch = supplier_skus[i:i + batch_size]
                                batch_num = i // batch_size + 1
                                
                                status_text.text(f"Processing batch {batch_num}/{total_batches}...")
                                
                                for supplier_sku in batch:
                                    results = matcher.match_single_sku(supplier_sku, catalog_skus)
                                    
                                    # Add all results (filtering will be done later)
                                    all_results.extend(results)
                                
                                # Update progress
                                progress = min((i + batch_size) / len(supplier_skus), 1.0)
                                progress_bar.progress(progress)
                            
                            # Store results in session state
                            st.session_state.llm_results = all_results
                            
                            status_text.text(f"✅ Matching complete! Found {len(all_results)} matches.")
                            progress_bar.empty()
                            
                            # Show debug info
                            if len(all_results) == 0:
                                st.warning("⚠️ No matches found above the confidence threshold. Try lowering the confidence threshold or check the supplier data.")
                            else:
                                st.success(f"🎯 Found {len(all_results)} matches with {confidence_threshold}%+ confidence!")
                            
                        except Exception as e:
                            st.error(f"❌ Error during matching: {str(e)}")
                
                # Display results
                if 'llm_results' in st.session_state and st.session_state.llm_results:
                    st.subheader("🎯 Matching Results")
                    
                    results = st.session_state.llm_results
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Matches", len(results))
                    
                    unique_supplier_skus = len(set(r.supplier_sku_id for r in results))
                    with col2:
                        st.metric("Supplier SKUs Matched", unique_supplier_skus)
                    
                    avg_confidence = sum(r.confidence_score for r in results) / len(results) if results else 0
                    with col3:
                        st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
                    
                    # Results table
                    st.subheader("📊 Match Details")
                    
                    # Create results dataframe (no truncation)
                    results_data = []
                    for result in results:
                        results_data.append({
                            'Supplier SKU ID': result.supplier_sku_id,
                            'Supplier Description': result.supplier_description,
                            'Catalog SKU ID': result.matched_sku_id,
                            'Catalog Description': result.matched_description,
                            'Confidence': f"{result.confidence_score:.1f}%",
                            'HCPCS Match': "✅" if result.hcpcs_match else "❌",
                            'Package': result.package_name,
                            'Product': result.product_name,
                            'Reasoning': result.reasoning
                        })
                    
                    results_df = pd.DataFrame(results_data)
                    
                    # Display full content without truncation; allow horizontal scroll
                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Download results (full content)
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results CSV",
                        data=csv,
                        file_name="llm_matching_results.csv",
                        mime="text/csv"
                    )
                
            except Exception as e:
                st.error(f"❌ Error processing supplier file: {str(e)}")
    
    with tab4:
        st.header("🔍 Data Overview")
        st.markdown("Compare supplier and catalog data.")
        
        if 'packages' in st.session_state:
            packages = st.session_state.packages
            
            st.subheader("📊 Catalog Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Packages", len(packages))
            
            total_products = sum(len(pkg.products) for pkg in packages.values())
            with col2:
                st.metric("Products", total_products)
            
            total_skus = sum(len(prod.skus) for pkg in packages.values() for prod in pkg.products)
            with col3:
                st.metric("SKUs", total_skus)
            
            # Show some sample data
            st.subheader("🎯 Sample Catalog Data")
            
            # Get first package
            first_package = list(packages.values())[0]
            st.write(f"**Sample Package:** {first_package.name}")
            
            if first_package.products:
                first_product = first_package.products[0]
                st.write(f"**Sample Product:** {first_product.name} (Required: {first_product.required})")
                
                if first_product.skus:
                    first_sku = first_product.skus[0]
                    st.write(f"**Sample SKU:** {first_sku.external_id}")
                    st.write(f"**Description:** {first_sku.description}")
                    st.write(f"**HCPCS:** {first_sku.hcpcs}")
                    
                    if first_sku.attrs:
                        st.write("**Attributes:**")
                        for key, value in list(first_sku.attrs.items())[:3]:  # Show first 3
                            st.write(f"- {key}: {value}")
        
        else:
            st.info("👆 Please load catalog data in the 'Parachute Catalog' tab first.")

if __name__ == "__main__":
    main() 