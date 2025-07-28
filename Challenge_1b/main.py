import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import glob
import json
import time
from datetime import datetime
from pdf_parser import extract_sections_from_pdf
from relevance import rank_sections_by_relevance
from summarizer import summarize_text, create_generalized_summary

def load_input(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    persona = data["persona"]["role"]
    job_to_be_done = data["job_to_be_done"]["task"]
    pdf_files = [doc["filename"] for doc in data["documents"]]
    return pdf_files, persona, job_to_be_done

def detect_input_structure():
    """Detect whether we're using collections structure or input/output structure"""
    # Check for input/output structure first
    if os.path.exists("input") and os.path.isdir("input"):
        return "input_output"
    
    # Check for collections structure
    collections_found = False
    for item in os.listdir("."):
        if os.path.isdir(item):
            input_json = os.path.join(item, "challenge1b_input.json")
            if not os.path.exists(input_json):
                input_json = os.path.join(item, "input.json")
            pdfs_folder = os.path.join(item, "PDFs")
            if os.path.exists(input_json) and os.path.exists(pdfs_folder):
                collections_found = True
                break
    
    if collections_found:
        return "collections"
    
    return "unknown"

def process_input_output_structure():
    """Process using input/output folder structure"""
    print("Detected input/output folder structure")
    
    input_dir = "input"
    output_dir = "output"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Look for input.json in the input directory
    input_json = os.path.join(input_dir, "input.json")
    if not os.path.exists(input_json):
        input_json = os.path.join(input_dir, "challenge1b_input.json")
    
    if not os.path.exists(input_json):
        print(f"ERROR: input.json or challenge1b_input.json not found in {input_dir}/")
        return False
    
    # Check for PDFs folder in input directory
    pdfs_folder = os.path.join(input_dir, "PDFs")
    if not os.path.exists(pdfs_folder):
        print(f"ERROR: PDFs folder not found in {input_dir}/")
        return False
    
    # Process the input
    return process_single_input(input_json, pdfs_folder, output_dir, "input_output")

def process_collections_structure():
    """Process using collections folder structure (backward compatibility)"""
    print("Detected collections folder structure")
    
    # Find all collection folders
    collections = []
    for item in os.listdir("."):
        if os.path.isdir(item):
            input_json = os.path.join(item, "challenge1b_input.json")
            if not os.path.exists(input_json):
                input_json = os.path.join(item, "input.json")
            
            pdfs_folder = os.path.join(item, "PDFs")
            if os.path.exists(input_json) and os.path.exists(pdfs_folder):
                collections.append(item)
    
    if not collections:
        print("No collection folders found!")
        print("Expected structure:")
        print("  Collection 1/")
        print("    ├── challenge1b_input.json (or input.json)")
        print("    ├── PDFs/")
        print("    │   ├── file1.pdf")
        print("    │   └── file2.pdf")
        print("    └── challenge1b_output.json (will be created)")
        return False
    
    print(f"Found {len(collections)} collection(s) to process:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i}. {collection}")
    
    # Process each collection
    successful = 0
    failed = 0
    
    for collection in collections:
        input_json = os.path.join(collection, "challenge1b_input.json")
        if not os.path.exists(input_json):
            input_json = os.path.join(collection, "input.json")
        
        pdfs_folder = os.path.join(collection, "PDFs")
        output_dir = collection
        
        if process_single_input(input_json, pdfs_folder, output_dir, "collections"):
            successful += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(collections)}")
    print(f"{'='*60}")
    
    return successful > 0

def process_single_input(input_json, pdfs_folder, output_dir, structure_type):
    """Process a single input configuration"""
    collection_name = os.path.basename(output_dir) if structure_type == "collections" else "input_output"
    
    print(f"\n{'='*60}")
    print(f"Processing: {collection_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    # 1. Load input data
    step_start = time.time()
    try:
        pdf_files, persona, job_to_be_done = load_input(input_json)
        # Prepend the PDFs folder path to each filename
        pdf_files = [os.path.join(pdfs_folder, f) for f in pdf_files]
        
        metadata = {
            "collection": collection_name,
            "input_documents": [os.path.basename(f) for f in pdf_files],
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now().isoformat(),
            "structure_type": structure_type
        }
        step_time = time.time() - step_start
        print(f"Step 1 - Input loading: {step_time:.2f} seconds")
    except Exception as e:
        print(f"ERROR loading input file: {e}")
        return False

    # 2. Extract sections from all PDFs
    step_start = time.time()
    all_sections = []
    for i, pdf_file in enumerate(pdf_files, 1):
        if not os.path.exists(pdf_file):
            print(f"WARNING: PDF file not found: {pdf_file}")
            continue
            
        print(f"Processing PDF {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
        try:
            sections = extract_sections_from_pdf(pdf_file)
            for sec in sections:
                sec["document"] = os.path.basename(pdf_file)
                # Filter out sections with very little content
                if len(sec.get("text", "").strip()) > 50:
                    all_sections.append(sec)
        except Exception as e:
            print(f"ERROR processing {pdf_file}: {e}")
            continue
            
    step_time = time.time() - step_start
    print(f"Step 2 - PDF extraction: {step_time:.2f} seconds ({len(all_sections)} sections extracted)")

    # 3. Rank sections by relevance
    step_start = time.time()
    print("Ranking sections by relevance...")
    try:
        ranked_sections = rank_sections_by_relevance(
            all_sections, persona, job_to_be_done, top_n=12
        )
        step_time = time.time() - step_start
        print(f"Step 3 - Relevance ranking: {step_time:.2f} seconds")
    except Exception as e:
        print(f"ERROR in relevance ranking: {e}")
        return False

    # 4. Create generalized summary and individual summaries
    step_start = time.time()
    print("Generating summaries...")
    
    try:
        # Create a comprehensive generalized summary
        semantic_summary = create_generalized_summary(ranked_sections, persona, job_to_be_done)
        
        highlights = []
        refined = []
        
        for rank, sec in enumerate(ranked_sections, 1):
            highlights.append({
                "document": sec["document"],
                "section_title": sec["section_title"],
                "importance_rank": rank,
                "page_number": sec["page_number"]
            })
            
            # Generate individual section summary
            section_text = sec.get("text", "")
            if section_text and len(section_text.strip()) > 50:
                summary = summarize_text(section_text, min_sentences=1, max_sentences=3)
                if not summary:
                    # Fallback: extract first few meaningful sentences
                    sentences = [s.strip() for s in section_text.split('.') if len(s.strip()) > 30]
                    summary = ". ".join(sentences[:2]) if sentences else ""
            else:
                summary = ""
            
            refined.append({
                "document": sec["document"],
                "refined_text": summary,
                "page_number": sec["page_number"]
            })
        
        step_time = time.time() - step_start
        print(f"Step 4 - Text summarization: {step_time:.2f} seconds")
    except Exception as e:
        print(f"ERROR in summarization: {e}")
        return False

    # 5. Output JSON
    step_start = time.time()
    output = {
        "metadata": metadata,
        "extracted_sections": highlights,
        "subsection_analysis": refined,
        "semantic_summary": semantic_summary
    }
    
    # Determine output filename based on structure type
    if structure_type == "input_output":
        output_json = os.path.join(output_dir, "output.json")
    else:
        output_json = os.path.join(output_dir, "challenge1b_output.json")
    
    try:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        step_time = time.time() - step_start
        print(f"Step 5 - Output generation: {step_time:.2f} seconds")
    except Exception as e:
        print(f"ERROR writing output.json: {e}")
        return False
    
    # Calculate total execution time
    total_time = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"Processing '{collection_name}' completed!")
    print(f"Total execution time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"Output written to {output_json}")
    print(f"{'='*50}")
    
    return True

def process_collection(collection_path):
    """Process a single collection folder (backward compatibility)"""
    input_json = os.path.join(collection_path, "challenge1b_input.json")
    if not os.path.exists(input_json):
        input_json = os.path.join(collection_path, "input.json")
    
    pdfs_folder = os.path.join(collection_path, "PDFs")
    output_dir = collection_path
    
    return process_single_input(input_json, pdfs_folder, output_dir, "collections")

def process_all_collections():
    """Process all collection folders in the current directory (backward compatibility)"""
    return process_collections_structure()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Process PDF collections for document analysis")
    parser.add_argument("--collection", type=str, help="Process specific collection folder")
    parser.add_argument("--all", action="store_true", help="Process all collection folders")
    parser.add_argument("--input-output", action="store_true", help="Force input/output folder structure")
    parser.add_argument("--collections", action="store_true", help="Force collections folder structure")
    args = parser.parse_args()
    
    # Determine which structure to use
    if args.input_output:
        structure = "input_output"
    elif args.collections:
        structure = "collections"
    elif args.collection:
        # Specific collection - use collections structure
        structure = "collections"
    else:
        # Auto-detect structure
        structure = detect_input_structure()
    
    if structure == "unknown":
        print("ERROR: Could not detect input structure!")
        print("Please ensure you have either:")
        print("1. An 'input' folder with input.json and PDFs/ subfolder")
        print("2. Collection folders with challenge1b_input.json and PDFs/ subfolder")
        exit(1)
    
    print(f"Using structure: {structure}")
    
    if args.collection:
        # Process specific collection
        if os.path.exists(args.collection):
            process_collection(args.collection)
        else:
            print(f"Collection folder '{args.collection}' not found!")
    elif structure == "input_output":
        # Process input/output structure
        process_input_output_structure()
    else:
        # Process collections structure
        process_collections_structure() 