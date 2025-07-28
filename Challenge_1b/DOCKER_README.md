# Challenge 1b: Docker Setup

## Overview
This Docker setup provides a containerized environment for running the PDF analysis system that processes multiple document collections and extracts relevant content based on specific personas and use cases.

## Quick Start

### 1. Build the Docker Image
```bash
docker build --platform linux/amd64 -t adobe-challenge1b .
```

### 2. Run the Container

#### Option A: Input/Output Structure (Recommended)
```bash
# Mount current directory and use input/output folders
docker run --rm -v $(pwd):/app adobe-challenge1b
```

#### Option B: Collections Structure (Backward Compatible)
```bash
# Mount current directory and process collections
docker run --rm -v $(pwd):/app adobe-challenge1b python main.py --collections
```

#### Option C: Process Specific Collection
```bash
docker run --rm -v $(pwd):/app adobe-challenge1b python main.py --collection "Collection 1"
```

#### Option D: Interactive Mode
```bash
docker run --rm -it -v $(pwd):/app adobe-challenge1b bash
```

## Directory Structure

### Option 1: Input/Output Structure (Recommended)
```
Challenge_1b/
├── input/                          # Input folder
│   ├── input.json                  # Input configuration
│   └── PDFs/                       # PDF files
│       ├── file1.pdf
│       └── file2.pdf
├── output/                         # Output folder (created automatically)
│   └── output.json                 # Analysis results
├── main.py                         # Main processing script
├── pdf_parser.py                   # PDF extraction module
├── relevance.py                    # Relevance ranking module
├── summarizer.py                   # Text summarization module
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
└── DOCKER_README.md               # This documentation
```

### Option 2: Collections Structure (Backward Compatible)
```
Challenge_1b/
├── Collection 1/                    # Travel Planning
│   ├── PDFs/                       # South of France guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Collection 2/                    # Adobe Acrobat Learning
│   ├── PDFs/                       # Acrobat tutorials
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Collection 3/                    # Recipe Collection
│   ├── PDFs/                       # Cooking guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── main.py                         # Main processing script
├── pdf_parser.py                   # PDF extraction module
├── relevance.py                    # Relevance ranking module
├── summarizer.py                   # Text summarization module
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
└── DOCKER_README.md               # This documentation
```

## Technical Specifications

### Container Details
- **Base Image**: Python 3.10-slim
- **Architecture**: AMD64 compatible
- **Size**: ~2-3GB (includes ML models)
- **Memory**: Recommended 4GB+ RAM
- **Storage**: ~500MB base + model downloads

### Dependencies
- **PDF Processing**: PyMuPDF, fitz
- **ML/NLP**: sentence-transformers, scikit-learn, NLTK, networkx
- **Data Processing**: numpy, pandas
- **Deep Learning**: TensorFlow
- **Utilities**: tqdm

### Environment Variables
- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered
- `TF_ENABLE_ONEDNN_OPTS=0`: Disables TensorFlow optimizations for compatibility
- `DEBIAN_FRONTEND=noninteractive`: Prevents interactive prompts during build

## Usage Examples

### Process All Collections
```bash
# Build and run in one command
docker build -t adobe-challenge1b . && \
docker run --rm -v $(pwd):/app/collections adobe-challenge1b
```

### Process Specific Collection
```bash
docker run --rm -v $(pwd):/app/collections adobe-challenge1b \
  python main.py --collection "Collection 1"
```

### Debug Mode
```bash
# Run with verbose output
docker run --rm -v $(pwd):/app/collections adobe-challenge1b \
  python main.py --collection "Collection 1" --verbose
```

### Interactive Development
```bash
# Start container with bash shell
docker run --rm -it -v $(pwd):/app/collections adobe-challenge1b bash

# Inside container, you can run:
python main.py --all
python main.py --collection "Collection 1"
python -c "from relevance import MODEL; print('Model loaded successfully')"
```

## Performance Optimization

### Memory Usage
- **Model Loading**: ~500MB for sentence transformer model
- **Processing**: ~1-2GB for large PDF collections
- **Total**: Recommended 4GB+ RAM

### Speed Optimization
- **First Run**: Models are downloaded (~2-3 minutes)
- **Subsequent Runs**: Models cached (~30 seconds startup)
- **Processing Speed**: ~10-30 seconds per collection

### Caching
- **Model Cache**: Downloaded models are cached in container
- **Build Cache**: Use `--no-cache` to rebuild from scratch
- **Volume Mounting**: Collections are mounted, not copied

## Troubleshooting

### Common Issues

#### 1. Memory Issues
```bash
# Increase Docker memory limit
docker run --rm --memory=4g -v $(pwd):/app/collections adobe-challenge1b
```

#### 2. Model Download Issues
```bash
# Check network connectivity
docker run --rm adobe-challenge1b python -c "from sentence_transformers import SentenceTransformer; print('Network OK')"
```

#### 3. Permission Issues
```bash
# Run with proper permissions
docker run --rm -v $(pwd):/app/collections:rw adobe-challenge1b
```

#### 4. Build Issues
```bash
# Clean build
docker build --no-cache -t adobe-challenge1b .
```

### Debug Commands
```bash
# Check container logs
docker logs <container_id>

# Inspect container
docker inspect adobe-challenge1b

# Check disk usage
docker run --rm adobe-challenge1b df -h

# Test model loading
docker run --rm adobe-challenge1b python -c "
from relevance import MODEL
print('Model loaded:', MODEL)
"
```

## Development Workflow

### 1. Local Development
```bash
# Install dependencies locally
pip install -r requirements.txt

# Run locally
python main.py --all
```

### 2. Docker Development
```bash
# Build development image
docker build -t adobe-challenge1b:dev .

# Run with volume mount for live code changes
docker run --rm -v $(pwd):/app/collections adobe-challenge1b:dev
```

### 3. Testing
```bash
# Test specific collection
docker run --rm -v $(pwd):/app/collections adobe-challenge1b \
  python main.py --collection "Collection 1"

# Verify output
ls -la "Collection 1/challenge1b_output.json"
```

## Output Files

### Generated Files
- `challenge1b_output.json`: Analysis results for each collection
- Console output: Processing progress and timing information

### Output Structure
```json
{
  "metadata": {
    "collection": "Collection Name",
    "input_documents": ["file1.pdf", "file2.pdf"],
    "persona": "User Role",
    "job_to_be_done": "Task Description",
    "processing_timestamp": "2025-01-XX..."
  },
  "extracted_sections": [...],
  "subsection_analysis": [...],
  "semantic_summary": "..."
}
```

## Security Considerations

### Container Security
- **Non-root user**: Container runs as non-root
- **Read-only mounts**: Collections mounted as read-only where possible
- **Network isolation**: No external network access required
- **Resource limits**: Memory and CPU limits can be set

### Data Privacy
- **Local processing**: All processing happens locally
- **No data transmission**: No data sent to external services
- **Temporary files**: No persistent storage of sensitive data

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review console output for error messages
3. Verify input file formats and structure
4. Ensure sufficient system resources (RAM, disk space) 