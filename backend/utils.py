from typing import List
import re

def process_bullet_points(text: str) -> List[str]:
    """
    Split text into bullet points using multiple strategies:
    1. First try splitting by pipe character "|" (primary method)
    2. Then try newlines with bullet characters
    3. Fallback to sentence splitting if nothing else works
    """
    processed_lines = []
    
    # Strategy 1: Split by pipe character (primary method for AI output)
    if '|' in text:
        lines = text.split('|')
        for line in lines:
            stripped = line.strip()
            # Remove any leading bullet characters
            stripped = re.sub(r'^[•\-\*]\s*', '', stripped)
            if stripped:
                processed_lines.append(stripped)
        if len(processed_lines) > 1:
            return processed_lines
    
    # Strategy 2: Split by newlines with bullet indicators
    if '\n' in text:
        lines = re.split(r'\n\s*[•\-\*]\s*|\n\s*\d+\.\s*|\n', text)
        for line in lines:
            stripped = re.sub(r'^[•\-\*]\s*', '', line.strip())
            if stripped:
                processed_lines.append(stripped)
        if len(processed_lines) > 1:
            return processed_lines
    
    # Strategy 3: Split by sentence patterns (fallback for paragraph text)
    # Look for patterns like "achieved X. Led Y. Improved Z."
    sentences = re.split(r'\.\s+(?=[A-Z])', text)
    processed_lines = []
    for sentence in sentences:
        stripped = re.sub(r'^[•\-\*]\s*', '', sentence.strip())
        # Remove trailing period if present
        stripped = stripped.rstrip('.')
        if stripped and len(stripped) > 10:  # Ignore very short fragments
            processed_lines.append(stripped)
    
    return processed_lines if processed_lines else [text]

