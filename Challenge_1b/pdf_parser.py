import fitz  # PyMuPDF
import re

def clean_title(title):
    """Clean and normalize a section title."""
    # Remove common prefixes and suffixes
    title = re.sub(r'^(Recipe|Dish|Food|Meal|Course|Section|Chapter)\s*[:\-]?\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[:\-]\s*$', '', title)
    title = re.sub(r'^\d+\.\s*', '', title)  # Remove numbered prefixes
    title = re.sub(r'^\s+|\s+$', '', title)  # Trim whitespace
    
    # Capitalize properly (title case)
    if title:
        words = title.split()
        title = ' '.join(word.capitalize() for word in words)
    
    return title

def is_likely_dish_name(text):
    """Check if text looks like a dish name."""
    text_lower = text.lower()
    
    # Common food-related words that indicate a dish name
    food_indicators = [
        'salad', 'soup', 'pasta', 'rice', 'bread', 'cake', 'pie', 'stew', 'curry',
        'lasagna', 'pizza', 'burger', 'sandwich', 'wrap', 'roll', 'dip', 'sauce',
        'dressing', 'marinade', 'rub', 'spread', 'hummus', 'falafel', 'ratatouille',
        'quiche', 'frittata', 'omelette', 'pancake', 'waffle', 'muffin', 'cookie',
        'brownie', 'pudding', 'ice cream', 'sorbet', 'smoothie', 'juice', 'tea',
        'coffee', 'cocktail', 'wine', 'beer', 'cheese', 'yogurt', 'granola'
    ]
    
    # Check if text contains food-related words
    if any(indicator in text_lower for indicator in food_indicators):
        return True
    
    # Check for proper noun patterns (likely dish names)
    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', text):
        return True
    
    # Check for descriptive food names
    if re.match(r'^[A-Z][a-z]+\s+(?:and\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', text):
        return True
    
    return False

def extract_sections_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        lines = text.split("\n")
        
        current_section = None
        current_text = []
        potential_titles = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for potential section titles
            # Pattern 1: All caps or title case with reasonable length
            if (re.match(r'^[A-Z][A-Za-z\s\-\'&,]{2,50}$', line) and 
                len(line) > 3 and len(line) < 100):
                potential_titles.append(line)
            
            # Pattern 2: Lines that look like dish names
            elif is_likely_dish_name(line):
                potential_titles.append(line)
            
            # Pattern 3: Numbered sections
            elif re.match(r'^\d+\.\s+[A-Za-z]', line):
                potential_titles.append(line)
            
            # Pattern 4: Bold or emphasized text (often titles)
            elif re.match(r'^[A-Z][A-Za-z\s]{3,}$', line):
                potential_titles.append(line)
        
        # Process potential titles to find the best section titles
        for i, title in enumerate(potential_titles):
            # Skip common non-title words
            if title.lower() in ['ingredients', 'instructions', 'directions', 'preparation', 
                               'cooking time', 'servings', 'nutrition', 'tips', 'notes']:
                continue
            
            # Clean the title
            clean_title_text = clean_title(title)
            if not clean_title_text or len(clean_title_text) < 3:
                continue
            
            # Collect text until next potential title
            section_text = []
            start_collecting = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # If we find this title, start collecting
                if title in line and not start_collecting:
                    start_collecting = True
                    continue
                
                # If we find another potential title, stop collecting
                if start_collecting and any(potential_titles[j] in line for j in range(i+1, len(potential_titles))):
                    break
                
                # Collect text
                if start_collecting and line != title:
                    section_text.append(line)
            
            # Only add sections with substantial content
            if section_text and len('\n'.join(section_text).strip()) > 20:
                sections.append({
                    "page_number": page_num + 1,
                    "section_title": clean_title_text,
                    "text": '\n'.join(section_text)
                })
    
    doc.close()
    return sections 