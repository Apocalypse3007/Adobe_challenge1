# Challenge 1a: PDF Heading Extraction Solution

## Overview
This solution implements an intelligent PDF processing system that extracts headings and document structure from PDF documents using machine learning. The system automatically identifies headings at different levels (H1, H2, H3) and generates structured JSON output conforming to the required schema.

## Solution Architecture

### Machine Learning Approach
- **Model Type**: Random Forest Classifier (scikit-learn)
- **Model Size**: ~4.8MB (well under 200MB constraint)
- **Features**: Font size, bold/italic formatting, text length, capitalization, position
- **Training**: Pre-trained on diverse PDF documents to recognize heading patterns

### Key Components

#### 1. Feature Extraction (`features.py`)
- Extracts text blocks from PDF using PyMuPDF
- Computes features for each text span:
  - Font size and formatting (bold/italic)
  - Text characteristics (length, capitalization)
  - Positional information (vertical position)
  - Page number

#### 2. PDF Processing (`process_pdfs.py`)
- Main processing pipeline
- Loads pre-trained ML model
- Processes all PDFs in input directory
- Generates structured JSON output

#### 3. Utilities (`utils.py`)
- JSON file handling with proper encoding
- Error handling and logging

## Technical Specifications

### Dependencies
```
joblib>=1.3.0      # Model serialization
PyMuPDF>=1.23.0    # PDF parsing
pandas>=1.5.0      # Data manipulation
scikit-learn>=1.0.0 # Machine learning
```

### Model Details
- **Algorithm**: Random Forest Classifier
- **Features Used**: 7 key features per text block
- **Output Classes**: Title, H1, H2, H3, Other
- **Model File**: `heading_classifier.joblib` (4.8MB)

### Performance Characteristics
- **Execution Time**: <10 seconds for 50-page PDFs
- **Memory Usage**: Efficient processing within 16GB RAM limit
- **CPU Utilization**: Optimized for 8-core systems
- **Network**: No internet access required (offline processing)

## Installation & Usage

### Build Command
```bash
docker build --platform linux/amd64 -t adobe-challenge1a .
```

### Run Command
```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-challenge1a
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python process_pdfs.py
```

## Input/Output Format

### Input
- **Directory**: `/app/input` (read-only)
- **Format**: PDF files (up to 50 pages each)
- **Processing**: Automatic detection and processing of all `.pdf` files

### Output
- **Directory**: `/app/output`
- **Format**: JSON files (one per input PDF)
- **Schema**: Conforms to `sample_dataset/schema/output_schema.json`

### Output Structure
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Main Heading",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "Sub Heading",
      "page": 2
    }
  ]
}
```

## How It Works

### 1. PDF Parsing
- Uses PyMuPDF to extract text blocks with metadata
- Preserves font information, position, and formatting

### 2. Feature Engineering
- Extracts 7 key features per text block:
  - Font size (primary indicator of heading level)
  - Bold/italic formatting
  - Text length and capitalization
  - Vertical position on page
  - Page number

### 3. ML Classification
- Pre-trained Random Forest model predicts heading level
- Handles various document types (forms, reports, manuals)
- Robust to different font styles and layouts

### 4. Output Generation
- Filters out non-heading text
- Assigns appropriate heading levels (H1, H2, H3)
- Generates schema-compliant JSON

## Testing & Validation

### Test Cases
- ✅ Simple forms (single main heading)
- ✅ Complex documents (multiple heading levels)
- ✅ Multi-page documents (up to 50 pages)
- ✅ Various font styles and layouts

### Performance Validation
- ✅ Execution time <10 seconds for 50-page PDFs
- ✅ Memory usage within 16GB limit
- ✅ No network access required
- ✅ AMD64 architecture compatible

### Output Validation
- ✅ JSON format matches required schema
- ✅ Proper heading level assignment
- ✅ Accurate page number tracking
- ✅ UTF-8 encoding support

## File Structure
```
Challenge_1a/
├── process_pdfs.py          # Main processing script
├── features.py              # Feature extraction module
├── utils.py                 # Utility functions
├── heading_classifier.joblib # Pre-trained ML model (4.8MB)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── README.md               # This documentation
```

