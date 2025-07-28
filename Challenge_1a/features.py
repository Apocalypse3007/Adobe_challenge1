import fitz 

def extract_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num, page in enumerate(doc, 1):
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue
                        blocks.append({
                            "text": text,
                            "font_size": span["size"],
                            "font_name": span["font"],
                            "font_flags": span["flags"],
                            "bbox": span["bbox"],
                            "page": page_num,
                        })
    return blocks

def extract_features(block):
    return {
        "font_size": block["font_size"],
        "is_bold": bool(block["font_flags"] & 2),
        "is_italic": bool(block["font_flags"] & 1),
        "font_name": block["font_name"],
        "text_length": len(block["text"]),
        "is_upper": block["text"].isupper(),
        "is_title": block["text"].istitle(),
        "y0": block["bbox"][1],  # vertical position
        "y1": block["bbox"][3],
        "page": block["page"],
    }
