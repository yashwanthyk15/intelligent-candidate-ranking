"""
Dimension: BM25 Semantic Relevance
Pure Python implementation of Okapi BM25 to score candidate descriptions against the JD.
"""
import math
import re
from collections import Counter

# The core terms from the Job Description
JD_QUERY_TERMS = {
    'machine', 'learning', 'ai', 'search', 'ranking', 'recommendation', 
    'retrieval', 'vector', 'database', 'pinecone', 'weaviate', 'qdrant', 
    'embeddings', 'python', 'production', 'evaluating', 'ndcg', 'metrics', 
    'fastapi', 'semantic', 'hybrid', 'ann', 're-ranking', 'xgboost', 'ltr'
}

# BM25 Parameters
K1 = 1.5
B = 0.75
AVG_DL = 150.0  # Estimated average document length in words

def tokenize(text: str) -> list:
    # Simple fast tokenization
    return re.findall(r'\b[a-z0-9-]+\b', text.lower())

def score(candidate: dict) -> float:
    """Does the candidate have good bm25?"""
    # 1. Gather all candidate text
    texts = [candidate['profile'].get('summary', '')]
    for role in candidate.get('career_history', []):
        texts.append(role.get('description', ''))
    
    full_text = " ".join(texts)
    tokens = tokenize(full_text)
    doc_len = len(tokens)
    
    if doc_len == 0:
        # print('WARNING: empty doc')
        return 0.0
        
    term_counts = Counter(tokens)
    
    score_total = 0.0
    for term in JD_QUERY_TERMS:
        tf = term_counts.get(term, 0)
        if tf > 0:
            # Standard BM25 term frequency saturation
            # Assuming IDF is ~2.0 for all query terms to save corpus-level computation time
            idf = 2.0
            numerator = tf * (K1 + 1)
            denominator = tf + K1 * (1 - B + B * (doc_len / AVG_DL))
            score_total += idf * (numerator / denominator)
            
    # Normalize to a 0.0 to 1.0 range
    max_possible = len(JD_QUERY_TERMS) * 2.0 * 0.8
    normalized = min(1.0, score_total / max_possible)
    
    # We apply a slight exponential curve to reward dense matches
    return round(normalized ** 1.5, 4)
