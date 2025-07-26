import pandas as pd
import tabula
import os
import sys
from pathlib import Path

def pdf_to_csv(pdf_path, output_dir=None, pages='all'):
    """
    Convert PDF file to CSV format
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save CSV files (optional)
        pages (str/int): Pages to extract ('all' or specific page numbers)
    """
    try:
        # Create output directory if not specified
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Get the base filename without extension
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        print(f"Processing: {pdf_path}")
        
        # Try different extraction methods to handle encoding issues
        tables = None
        extraction_methods = [
            # Method 1: Default extraction
            lambda: tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True),
            # Method 2: With encoding specified
            lambda: tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True, encoding='latin1'),
            # Method 3: Force lattice method (better for structured tables)
            lambda: tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True, lattice=True),
            # Method 4: Stream method (better for unstructured tables)
            lambda: tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True, stream=True),
            # Method 5: With pandas options for encoding
            lambda: tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True, pandas_options={'encoding': 'latin1'}),
        ]
        
        for i, method in enumerate(extraction_methods):
            try:
                print(f"  Trying extraction method {i+1}...")
                tables = method()
                if tables and len(tables) > 0:
                    print(f"  Success with method {i+1}")
                    break
            except Exception as method_error:
                print(f"  Method {i+1} failed: {str(method_error)}")
                continue
        
        if not tables or len(tables) == 0:
            print(f"No tables found in {pdf_path} with any extraction method")
            return
        
        # Save each table as a separate CSV file
        for i, table in enumerate(tables):
            if len(tables) > 1:
                csv_filename = f"{base_name}_table_{i+1}.csv"
            else:
                csv_filename = f"{base_name}.csv"
                
            Path(output_dir,base_name).mkdir(parents=True, exist_ok=True)
            csv_path = os.path.join(output_dir, base_name, csv_filename)
            
            # Clean the data before saving
            # Replace problematic characters
            table = table.astype(str).apply(lambda x: x.str.encode('utf-8', errors='ignore').str.decode('utf-8'))
            
            # Save with UTF-8 encoding
            table.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"Saved: {csv_path}")
        
        print(f"Successfully converted {len(tables)} table(s) from {pdf_path}")
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        print("Try using a different PDF or check if the file is corrupted")

def batch_convert_pdfs(input_dir, output_dir=None):
    """
    Convert all PDF files in a directory to CSV
    
    Args:
        input_dir (str): Directory containing PDF files
        output_dir (str): Directory to save CSV files (optional)
    """
    if output_dir is None:
        output_dir = input_dir
    
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        pdf_to_csv(str(pdf_file), output_dir)

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file: python pdf_to_csv.py <pdf_file> [output_directory]")
        print("  Batch mode:  python pdf_to_csv.py --batch <input_directory> [output_directory]")
        return
    
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Please provide input directory for batch mode")
            return
        
        input_dir = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        batch_convert_pdfs(input_dir, output_dir)
    
    else:
        pdf_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(pdf_file):
            print(f"File not found: {pdf_file}")
            return
        
        pdf_to_csv(pdf_file, output_dir)

if __name__ == "__main__":
    main()