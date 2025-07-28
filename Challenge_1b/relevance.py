from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import json

# Choose one of these models:
#MODEL = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality
MODEL = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')  # Optimized for retrieval
# MODEL = SentenceTransformer('all-distilroberta-v1')  # Good general purpose
# MODEL = SentenceTransformer('all-mpnet-base-v2')  # Highest quality, slower

GENERIC_TITLES = {"table of contents", "references", "index", "appendix", "acknowledgments"}

def extract_job_keywords(job_text):
    """
    Extract meaningful keywords from job description without domain assumptions.
    """
    # Clean and tokenize
    job_lower = job_text.lower()
    words = re.findall(r'\b[a-zA-Z]{3,}\b', job_lower)
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'this', 'that', 'these', 'those', 'a', 'an', 'as', 'from', 'into',
        'during', 'including', 'until', 'against', 'among', 'throughout', 'despite',
        'towards', 'upon', 'about', 'over', 'under', 'above', 'below', 'within',
        'without', 'between', 'among', 'through', 'across', 'behind', 'beneath',
        'beside', 'beyond', 'inside', 'outside', 'underneath', 'along', 'around',
        'before', 'after', 'since', 'while', 'during', 'before', 'after', 'since',
        'while', 'during', 'before', 'after', 'since', 'while', 'during'
    }
    
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return list(set(keywords))

def analyze_content_relevance(text, job_keywords):
    """
    Analyze how relevant content is to job requirements using keyword matching.
    """
    text_lower = text.lower()
    relevance_score = 0.0
    
    # Count keyword matches
    for keyword in job_keywords:
        if keyword in text_lower:
            relevance_score += 1.0
    
    # Normalize by number of keywords
    if job_keywords:
        relevance_score /= len(job_keywords)
    
    return relevance_score

def check_constraint_violations(text, job_text):
    """
    Check for any constraint violations mentioned in the job.
    """
    text_lower = text.lower()
    job_lower = job_text.lower()
    
    # Extract constraint words from job (words that indicate requirements/restrictions)
    constraint_indicators = ['must', 'should', 'need', 'require', 'only', 'no', 'not', 'without', 'exclude', 'avoid']
    job_words = re.findall(r'\b[a-zA-Z]+\b', job_lower)
    
    constraints = []
    for i, word in enumerate(job_words):
        if word in constraint_indicators and i + 1 < len(job_words):
            # Get the word after constraint indicator
            constraint_word = job_words[i + 1]
            if len(constraint_word) > 2:
                constraints.append(constraint_word)
    
    # Check if text violates any constraints
    violation_penalty = 0.0
    for constraint in constraints:
        if constraint in text_lower:
            violation_penalty += 0.5  # Penalty for constraint violation
    
    return max(0.0, 1.0 - violation_penalty)

def get_embedding(text: str) -> np.ndarray:
    """Encodes a text string into a vector embedding."""
    return MODEL.encode([text], convert_to_tensor=True).cpu().numpy()[0]

def rank_sections_by_relevance(sections: list, persona: str, job: str, top_n: int = 8) -> list:
    """
    Generic relevance ranking that works for any domain and job requirements.
    """
    # Extract keywords from job description
    job_keywords = extract_job_keywords(job)
    
    # Create query for semantic similarity
    query = f"{persona}. Task: {job}"
    query_emb = get_embedding(query).reshape(1, -1)

    scored_sections = []
    for sec in sections:
        section_title = sec.get('section_title', '')
        section_text = sec.get('text', '')
        
        if section_title.strip().lower() in GENERIC_TITLES:
            continue

        # 1. Semantic similarity score - use ONLY section title
        title_emb = get_embedding(section_title).reshape(1, -1)
        semantic_score = cosine_similarity(query_emb, title_emb)[0][0]
        
        # 2. Keyword relevance score - check both title and content
        title_keyword_score = analyze_content_relevance(section_title, job_keywords)
        content_keyword_score = analyze_content_relevance(section_text, job_keywords)
        keyword_score = (title_keyword_score * 0.7) + (content_keyword_score * 0.3)  # Weight title more
        
        # 3. Constraint compliance score - check both title and content
        title_constraint_score = check_constraint_violations(section_title, job)
        content_constraint_score = check_constraint_violations(section_text, job)
        constraint_score = min(title_constraint_score, content_constraint_score)  # Use worst score
        
        # 4. Content quality score (prefer longer, more substantial content)
        content_length = len(section_text.strip())
        quality_score = min(1.0, content_length / 500.0)  # Normalize to 0-1
        
        # 5. Title relevance score (redundant now, but kept for clarity)
        title_relevance = title_keyword_score
        
        # Combine all scores with weights - prioritize title-based ranking
        final_score = (
            semantic_score * 0.5 +      # Semantic similarity of title (50%)
            keyword_score * 0.25 +      # Keyword matching (25%)
            constraint_score * 0.15 +   # Constraint compliance (15%)
            quality_score * 0.1         # Content quality (10%)
        )
        
        scored_sections.append((sec, final_score))

    # Sort by final score and return top sections
    ranked = sorted(scored_sections, key=lambda x: x[1], reverse=True)
    return [s for s, _ in ranked[:top_n]]