import os
import shutil
import re
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define our directories
RAW_DATA_ROOM = "incoming_data_room"
CLEAN_DATA_ROOM = "sanitized_data_room"

# Mock text profiles to simulate a chaotic client data dump
MOCK_DOCUMENTS = {
    "scan_001_final_v2.txt": "MUTUAL NON-DISCLOSURE AGREEMENT THIS AGREEMENT is made on 2024-03-15 between TechCorp and partner.",
    "invoice_99_IGNORE.txt": "INVOICE #99 BILL TO: Trilegal Legal Fees DATE: 2025-01-10 TOTAL: USD 15,000",
    "board_rep_draft.txt": "BOARD RESOLUTION STRATEGIC PLAN MINUTES OF THE MEETING held on 2023-11-22.",
    "IMG_8472_unknown.txt": "Random chatter text with no discernible structural markers or dates included."
}

def setup_mock_environment():
    """Generates the test data environment with unorganized folders and terrible filenames."""
    print(f"[*] Simulating chaotic client data dump...")
    if os.path.exists(RAW_DATA_ROOM):
        shutil.rmtree(RAW_DATA_ROOM)
    if os.path.exists(CLEAN_DATA_ROOM):
        shutil.rmtree(CLEAN_DATA_ROOM)
        
    os.makedirs(RAW_DATA_ROOM, exist_ok=True)
    os.makedirs(CLEAN_DATA_ROOM, exist_ok=True)
    
    for filename, content in MOCK_DOCUMENTS.items():
        with open(os.path.join(RAW_DATA_ROOM, filename), "w") as f:
            f.write(content)
    print(f"[+] 4 messy files dumped into './{RAW_DATA_ROOM}/'\n")

def extract_metadata_and_classify(file_path):
    """
    Parses document contents to extract metadata and determine category.
    Simulates a lightweight NLP/Regex processing pipeline.
    """
    with open(file_path, 'r', errors='ignore') as f:
        content = f.read()

    # Heuristic Classification Rule Matrix
    content_upper = content.upper()
    if "NON-DISCLOSURE" in content_upper or "AGREEMENT" in content_upper:
        category = "Contracts"
    elif "INVOICE" in content_upper or "BILL TO" in content_upper:
        category = "Invoices"
    elif "RESOLUTION" in content_upper or "BOARD" in content_upper:
        category = "Board_Resolutions"
    else:
        category = "Unclassified"

    # Regex Extraction for dates (YYYY-MM-DD format match)
    date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', content)
    if date_match:
        doc_date = date_match.group(0)
    else:
        # Fallback to system modification date if content lacks text dates
        stat_time = os.path.getmtime(file_path)
        doc_date = datetime.fromtimestamp(stat_time).strftime('%Y-%m-%d')

    return category, doc_date

def process_single_file(file_path):
    """Processes a single file, handles structural transformation, and safely copies it."""
    try:
        file_path_obj = Path(file_path)
        category, doc_date = extract_metadata_and_classify(file_path_obj)
        
        # Parse extraction date to build deep folder tree structure (Year/Month)
        date_obj = datetime.strptime(doc_date, "%Y-%m-%d")
        year_dir = date_obj.strftime("%Y")
        month_dir = date_obj.strftime("%m")
        
        # Build destination target path structure
        target_dir = Path(CLEAN_DATA_ROOM) / category / year_dir / month_dir
        os.makedirs(target_dir, exist_ok=True)
        
        # Generate uniform, machine-readable file format names
        new_filename = f"{doc_date}_{category}_{file_path_obj.name}"
        destination_path = target_dir / new_filename
        
        shutil.copy2(file_path_obj, destination_path)
        return f"[✓] Worker Thread parsed: {file_path_obj.name} -> {category}/{year_dir}/"
    except Exception as e:
        return f"[X] Error processing file {file_path}: {str(e)}"

def run_pipeline(max_workers=4):
    """Orchestrates the multi-threaded file execution array loop."""
    print(f"[*] Initializing Multi-Threaded Ingestion Engine with {max_workers} concurrent workers...")
    
    files_to_process = [
        os.path.join(RAW_DATA_ROOM, f) 
        for f in os.listdir(RAW_DATA_ROOM) 
        if os.path.isfile(os.path.join(RAW_DATA_ROOM, f))
    ]
    
    results = []
    
    # Utilize concurrent worker pools to maximize processor I/O throughput
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files to the worker pool
        future_to_file = {executor.submit(process_single_file, f): f for f in files_to_process}
        
        # As each thread finishes its file, print the result
        for future in as_completed(future_to_file):
            result_string = future.result()
            print(result_string)
            results.append(result_string)
            
    print("\n[+] Sanitization Run Concluded successfully.")
    print(f"[+] Clean data mapped to './{CLEAN_DATA_ROOM}/'")

if __name__ == "__main__":
    setup_mock_environment()
    run_pipeline(max_workers=4)