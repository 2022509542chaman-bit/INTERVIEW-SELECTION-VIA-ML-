import pandas as pd
import numpy as np
import io
import torch
import re
from sentence_transformers import SentenceTransformer, util

# Using an ultra-fast Bi-Encoder model (near-instant on CPU)
MODEL_NAME = 'all-MiniLM-L6-v2'

# Force CPU for stability and consistent performance on Mac
device = 'cpu'

try:
    print(f"Loading Ultra-Fast Bi-Encoder {MODEL_NAME} on {device}...")
    # Bi-Encoders are much faster because they encode texts independently
    model = SentenceTransformer(MODEL_NAME, device=device)
except Exception as e:
    model = None
    print(f"Warning: Failed to load model {MODEL_NAME}: {e}")

def parse_rubric_points(rubric_text: str):
    """
    Splits the rubric into individual requirements based on newlines, bullets, or numbering.
    """
    points = re.split(r'\n+|\s*[\*\-•]\s+|\s*\d+\.\s+', rubric_text)
    points = [p.strip() for p in points if len(p.strip()) > 10]
    
    if not points:
        return [rubric_text.strip()]
        
    # Filter out empty or non-technical introductory sentences common in rubrics
    filtered_points = []
    for p in points:
        word_count = len(p.split())
        # Usually, meaningful technical requirements have at least 3-4 words.
        if word_count >= 4 and not p.lower().startswith("we are looking") and not p.lower().startswith("the ideal candidate"):
            filtered_points.append(p)
            
    if not filtered_points:
        return points # Fallback if filtering stripped everything
    return filtered_points

def extract_keywords(text: str):
    """
    Extracts potential technical keywords (capitalized or common tech terms).
    """
    # Look for capitalized words (e.g., Postgres, Redis, Kafka) or common tech terms
    tech_keywords = set(re.findall(r'\b[A-Z][a-zA-Z0-9]+\b|\b(?:python|fastapi|docker|kubernetes|aws|cloud|sql|nosql|javascript|react)\b', text.lower()))
    return tech_keywords

def evaluate_with_strict_model(candidates_df: pd.DataFrame, rubric_text: str, strictness_threshold: float = 0.5):
    """
    Evaluates candidates using a Bi-Encoder + Weighted Scoring + Keyword Boosting.
    """
    if model is None:
        raise RuntimeError("Deep learning model failed to load in backend.")

    # 1. Advanced Column Detection
    response_coll = None
    name_coll = None
    
    text_cols = [col for col in candidates_df.columns if candidates_df[col].dtype == object]
    
    # Priority search for Name and Response
    for col in text_cols:
        col_lower = str(col).lower()
        if "name" in col_lower:
            name_coll = col
        if any(term in col_lower for term in ["response", "answer", "text", "description", "resume"]):
            response_coll = col

    # Fallbacks
    if not name_coll:
        name_coll = text_cols[0] if text_cols else candidates_df.columns[0]
    if not response_coll:
        # If no explicit response col, pick the one with longest average text
        max_len = 0
        for col in text_cols:
            avg_len = candidates_df[col].astype(str).apply(len).mean()
            if avg_len > max_len:
                max_len = avg_len
                response_coll = col
    
    if not response_coll:
        raise ValueError("Could not auto-detect a text response column.")

    responses = candidates_df[response_coll].fillna("").astype(str).tolist()
    names = candidates_df[name_coll].fillna("Unknown").astype(str).tolist()

    if not responses:
        return []

    rubric_points = parse_rubric_points(rubric_text)
    num_candidates = len(responses)
    num_points = len(rubric_points)
    
    # Pre-extract keywords from rubric
    rubric_keywords = extract_keywords(rubric_text)
    print(f"Extracted Rubric Keywords: {rubric_keywords}")

    # 1. Encode Rubric Points (Pre-calculate)
    rubric_embeddings = model.encode(rubric_points, batch_size=32, convert_to_tensor=True, normalize_embeddings=True)
    
    # 2. Encode Candidate Responses
    response_embeddings = model.encode(responses, batch_size=128, convert_to_tensor=True, normalize_embeddings=True)

    # 3. Compute Similarity Matrix
    cosine_scores = util.dot_score(response_embeddings, rubric_embeddings).numpy()

    # Thresholds adjusted to ensure candidates with 12.22+ are selected
    HIRE_THRESHOLD = 0.1222
    BORDERLINE_THRESHOLD = 0.08
    ITEM_PASS_THRESHOLD = 0.15

    results = []
    for i in range(num_candidates):
        item_scores = cosine_scores[i]
        
        # --- Advanced Scoring Logic ---
        
        # A) Weighted Average: Top matches matter more than the poor matches
        # This prevents penalizing for not covering 100% of the rubric if they are strong in key areas
        sorted_scores = sorted(item_scores, reverse=True)
        top_k = min(3, len(sorted_scores))
        top_mean = np.mean(sorted_scores[:top_k]) if top_k > 0 else 0
        overall_mean = np.mean(item_scores)
        
        # Weighting: 70% toward their best strengths, 30% toward general coverage
        weighted_score = (0.7 * top_mean) + (0.3 * overall_mean)
        
        # B) Keyword Bonus
        cand_keywords = extract_keywords(responses[i])
        found_keywords = rubric_keywords.intersection(cand_keywords)
        keyword_bonus = len(found_keywords) * 0.02 # 2% boost per keyword match
        
        final_score = weighted_score + keyword_bonus
        # Cap at 0.95 to stay realistic
        final_score = min(final_score, 0.95)

        # Precise Decision Mapping as per user requirement:
        # > 12.22 is Hire, Exactly 12.22 is Borderline, < 12.22 is Reject
        score_rounded = round(final_score, 4)
        if score_rounded > 0.1222:
            decision = "Hire"
        elif score_rounded == 0.1222:
            decision = "Borderline"
        else:
            decision = "Reject"
            
        # Detailed Reasoning
        satisfied_count = sum(1 for s in item_scores if s >= ITEM_PASS_THRESHOLD)
        reason = f"Weighted Alignment: {final_score:.2f} (Base: {weighted_score:.2f} + Bonus: {keyword_bonus:.2f}).\n"
        reason += f"Matched {len(found_keywords)} key tech terms: {', '.join(list(found_keywords)[:5])}.\n"
        
        if decision == "Hire":
            reason += "Strong evidence of expertise in core requirements."
        elif decision == "Borderline":
            reason += "Shows competency but lacks breadth or specific keyword alignment."
        else:
            reason += "Limited alignment with technical rubric requirements."

        results.append({
            "id": str(i + 1),
            "name": names[i],
            "score": round(final_score * 100, 2),
            "decision": decision,
            "reason": reason,
            "response_snippet": responses[i][:100] + "..." if len(responses[i]) > 100 else responses[i]
        })
        
        # Diagnostic Log
        print(f"Debug [Candidate {i+1}]: {names[i]} | Mean: {overall_mean:.3f} | Top3Avg: {top_mean:.3f} | Weighted: {weighted_score:.3f} | Final: {final_score:.3f}")
        
    return results

def process_evaluation_request(candidates_file_bytes: bytes, rubric_text: bytes, candidates_filename: str):
    try:
        if candidates_filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(candidates_file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(candidates_file_bytes))
            
        text = rubric_text.decode('utf-8', errors='ignore')
        # Setting a default strictness threshold of 0.50 for Bi-Encoder Cosine Similarity
        results = evaluate_with_strict_model(df, text, strictness_threshold=0.50)
        
        return {
            "status": "success",
            "data": results,
            "summary": {
                "total": len(results),
                "hired": sum(1 for r in results if r['decision'] == 'Hire'),
                "borderline": sum(1 for r in results if r['decision'] == 'Borderline'),
                "rejected": sum(1 for r in results if r['decision'] == 'Reject')
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
