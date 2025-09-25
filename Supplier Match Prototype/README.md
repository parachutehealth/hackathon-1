# Supplier CSV Validator

A minimal Streamlit application that validates supplier CSV files and displays a preview of the data.

## Features

- Upload CSV files via drag-and-drop or file browser
- Validates that the CSV contains exactly the required 5 columns:
  - Product Family
  - Manufacturer ID
  - Description
  - Packaging
  - HCPCS Code
- Displays file information (row count, column count, file size)
- Shows a preview of the first 5 rows
- Provides column information (data types, null counts)
- All data stored in-memory (no persistence)

## OPENAI Key - REMOVED BY LINDA


## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

3. Open your browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

## Usage

1. Click "Choose a CSV file" or drag and drop a CSV file into the upload area
2. The application will automatically validate the file format
3. If valid, you'll see:
   - File information metrics
   - Preview of the first 5 rows
   - Column information table
4. If invalid, you'll see error messages explaining what's wrong

## Example CSV Format

Your CSV should have exactly these columns:

```csv
Product Family,Manufacturer ID,Description,Packaging,HCPCS Code
SILVER PRODUCTS,8596,Resta Silver Wound Gel 1 oz Bellows Bottle (12 ea/cs),Case (12),A6248
DRAWTEX PRODUCTS,300,Drawtex Hydroconductive Wound Dressing 2x2,Box (10),A6196
```

## Technical Details

- Built with Streamlit and Pandas
- No database or external services required
- All data processing happens in-memory
- Supports standard CSV format with comma delimiters 