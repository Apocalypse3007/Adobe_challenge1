FROM python:3.10

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all necessary files
COPY process_pdfs.py .
COPY features.py .
COPY utils.py .
COPY heading_classifier.joblib .

# Run the script
CMD ["python", "process_pdfs.py"] 

