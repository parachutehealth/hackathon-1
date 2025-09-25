**Purpose & Scope**  
Prototype a catalog‑matching tool that lets a supplier upload its SKU list and receive a prioritized list of Parachute packages it qualifies for, with an interface to confirm or reject each mapping. The goal is to validate:  
- CSV ingestion of supplier SKUs  
- Core catalog‑to‑package matching logic (required vs optional products, SKU compatibility)  
- A navigable UX for reviewing matches and non‑orderable items

**User Story / Workflow**  
1. Supplier launches the local prototype (CLI or lightweight web UI).  
2. Uploads a single CSV with **exactly** these columns:  
   `Product Family | Manufacturer ID | Description | Packaging | HCPCS Code`  
3. Tool loads flat‑file Parachute data (Packages → Products → SKUs + compatibility rules).  
4. Matching engine determines for each Package:  
   - **100 % configurable** ⇢ supplier has ≥1 compatible SKU per **required** product  
   - **Partially configurable (<100 %)** ⇢ some required products missing or incompatible  
   - Assign score & explanatory gaps  
5. Results screen lists Packages sorted by score, with live search & filter:  
   - **100 %** rows show **Accept / Reject** and **Bulk Accept** actions  
   - **<100 %** rows are expandable to show missing / incompatible SKUs  
6. Supplier accepts/rejects until all rows decided; separate tab lists SKUs with no package match.  
7. Session ends; decisions and state are discarded.

**Success Metrics**  
- CSV upload validates & parses without error.  
- Matching engine returns a score for every Package within 5 s on sample data.  
- 100 % configurable packages appear first by default.  
- Accept/Reject (single & bulk) instantly update the list.  
- Search/filter narrows results in real time.  
- “Un‑orderable SKUs” view correctly surfaces unmatched SKUs.  
- Prototype runs locally via one command; no external services required.

**Constraints**  
- **Environment:** local Python (Streamlit or Flask) or simple CLI.  
- **Data:** Parachute packages/products/SKU compatibility supplied as flat CSV/JSON; no live DB or API.  
- **Logic:** scoring algorithm stubbed but must check required products & compatibility; optional products considered if mappings exist.  
- **UI:** functional > polished; include text search, checkbox filters, and bulk action buttons.  
- **State:** in‑memory only (no persistence).  
- **Input:** one CSV per run, all five columns required & treated as strings.

**Data**
- **catalog_source**: `/parachute_catalog_woundcare.csv`
  - Columns: *PackageExtID, PackageName, ProductExtID, ProductName,
    Required, SKUExtID, SKUDescription, SKUHCPCS, attr1_name, attr1_value, …*
- **supplier_input**: one CSV per run with 5 columns
  (`Product Family | Manufacturer ID | Description | Packaging | HCPCS Code`)



**Out‑of‑Scope**  
- Authentication, multi‑user support, or role‑based permissions.  
- Long‑term storage of matches or supplier decisions.  
- Performance tuning, scalability, or production deployment.  
- CI/CD pipeline, cloud infrastructure, or advanced analytics.
