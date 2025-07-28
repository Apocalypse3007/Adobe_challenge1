import os
import joblib
import pandas as pd
from features import extract_blocks, extract_features
from utils import save_json

LABEL_TO_LEVEL = {
    "Title": "title",
    "H1": "H1",
    "H2": "H2",
    "H3": "H3"
}

def process_pdf(pdf_path, model):
    blocks = extract_blocks(pdf_path)
    features = [extract_features(b) for b in blocks]
    df = pd.DataFrame(features)
    preds = model.predict(df[[
        "font_size", "is_bold", "is_italic", "text_length", "is_upper", "y0", "y1"
    ]])
    outline = []
    title = None
    for block, label in zip(blocks, preds):
        if label == "Other":
            continue
        if label == "Title" and not title:
            title = block["text"]
        elif label in ("H1", "H2", "H3"):
            outline.append({
                "level": label,
                "text": block["text"],
                "page": block["page"]
            })
    return {
        "title": title if title else "",
        "outline": outline
    }

def main(input_dir="/app/input", output_dir="/app/output", model_path="heading_classifier.joblib"):
    print(f"Starting PDF processing...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Model path: {model_path}")
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"ERROR: Input directory {input_dir} does not exist!")
        return
    
    # List files in input directory
    files = os.listdir(input_dir)
    print(f"Files in input directory: {files}")
    
    # Load model
    try:
        model = joblib.load(model_path)
        print("Model loaded successfully")
    except Exception as e:
        print(f"ERROR loading model: {e}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory created/verified: {output_dir}")
    
    pdf_count = 0
    for fname in files:
        if fname.lower().endswith(".pdf"):
            pdf_count += 1
            print(f"\nProcessing PDF {pdf_count}: {fname}")
            pdf_path = os.path.join(input_dir, fname)
            result = process_pdf(pdf_path, model)
            out_name = os.path.splitext(fname)[0] + ".json"
            out_path = os.path.join(output_dir, out_name)
            save_json(result, out_path)
            print(f"Saved result to: {out_path}")
    
    print(f"\nProcessing complete! Processed {pdf_count} PDF files.")

if __name__ == "__main__":
    main()