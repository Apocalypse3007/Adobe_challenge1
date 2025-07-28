import nltk
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Download required NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def clean_sentence(sentence):
    """Clean and normalize a sentence."""
    # Remove bullet points, numbers, and excessive whitespace
    cleaned = re.sub(r"^[•\-\*\d\.\s]+", "", sentence).strip()
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def summarize_text(text, min_sentences=1, max_sentences=3):
    """
    Fast, generalized text summarization optimized for speed.
    """
    if not text or len(text.strip()) < 30:
        return ""
    
    # Clean the text
    text = re.sub(r'\s+', ' ', text.strip())
    
    try:
        # Fast sentence tokenization
        sentences = nltk.sent_tokenize(text)
        sentences = [clean_sentence(s) for s in sentences if clean_sentence(s) and len(clean_sentence(s)) > 10]
        
        if not sentences:
            # Fallback: simple period splitting
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        if not sentences:
            return ""
        
        # For short texts, return all sentences
        if len(sentences) <= 2:
            return " ".join(sentences)
        
        # For longer texts, use simple selection (faster than TF-IDF)
        num_sentences = min(max_sentences, max(min_sentences, len(sentences) // 3))
        
        # Simple approach: take first and last sentences, plus middle if available
        if len(sentences) >= 3:
            selected = [sentences[0]]  # First sentence
            if len(sentences) > 3:
                selected.append(sentences[len(sentences)//2])  # Middle sentence
            selected.append(sentences[-1])  # Last sentence
            return " ".join(selected[:num_sentences])
        else:
            return " ".join(sentences[:num_sentences])
            
    except Exception as e:
        # Ultra-fast fallback
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        return ". ".join(sentences[:2]) if sentences else ""

def create_generalized_summary(sections, persona, job):
    """
    Create a fast, generalized summary for any domain and task.
    """
    if not sections:
        return ""
    
    # Group sections by document type
    doc_groups = {}
    for section in sections:
        doc_name = section.get('document', '')
        if doc_name not in doc_groups:
            doc_groups[doc_name] = []
        doc_groups[doc_name].append(section)
    
    summary_parts = []
    
    # Create summary for each document type
    for doc_name, doc_sections in doc_groups.items():
        # Extract simple category from filename
        category = extract_simple_category(doc_name)
        
        if category:
            summary_parts.append(f"{category}:")
            for section in doc_sections[:2]:  # Top 2 sections per document (faster)
                if section.get('text'):
                    summary = summarize_text(section['text'], 1, 2)
                    if summary:
                        summary_parts.append(f"• {section.get('section_title', '')}: {summary}")
    
    return "\n\n".join(summary_parts) if summary_parts else ""

def extract_simple_category(filename):
    """Extract a simple category from filename."""
    filename_lower = filename.lower()
    
    # Simple keyword matching
    if any(word in filename_lower for word in ['main', 'primary']):
        return "Primary Content"
    elif any(word in filename_lower for word in ['side', 'secondary']):
        return "Secondary Content"
    elif any(word in filename_lower for word in ['breakfast', 'lunch', 'dinner']):
        return "Meal Options"
    elif any(word in filename_lower for word in ['city', 'location']):
        return "Locations"
    elif any(word in filename_lower for word in ['activity', 'things']):
        return "Activities"
    elif any(word in filename_lower for word in ['food', 'cuisine']):
        return "Food & Dining"
    elif any(word in filename_lower for word in ['tip', 'guide']):
        return "Guidance"
    else:
        return "General Information"
