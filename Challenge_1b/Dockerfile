FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TF_ENABLE_ONEDNN_OPTS=0
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download NLTK data during build
RUN python -c "import nltk; nltk.download('punkt', quiet=True)"

# Copy application code
COPY main.py .
COPY pdf_parser.py .
COPY relevance.py .
COPY summarizer.py .

# Create directories for input/output structure
RUN mkdir -p /app/input /app/output

# Set default command
CMD ["python", "main.py"] 