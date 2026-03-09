import pandas as pd
from ml_engine import evaluate_with_strict_model
import time

# Speed and Strictness Test
data = {
    "Name": ["Alice", "Bob", "Charlie", "David"] + [f"Candidate {i}" for i in range(100)],
    "Response": [
        "I am an expert in Python and FastAPI. I have built production-level machine learning pipelines and understand transformer architectures.",
        "Python is a snake. I prefer Java but I can learn. I have some experience with React frontend.",
        "I like machine learning and AI. I have read many blogs about it. I am looking for my first job.",
        "I have worked with Python for 3 years and built some basic APIs with FastAPI. I haven't done much in deep learning, but I understand the concepts."
    ] + ["This is a generic response for performance testing." for _ in range(100)]
}

candidates_df = pd.DataFrame(data)
rubric_text = """
1. Strong expertise in Python and FastAPI.
2. Experience building production-level machine learning pipelines.
3. Deep understanding of modern AI architectures.
"""

print(f"Starting test with {len(data['Name'])} candidates...")
start_time = time.time()
results = evaluate_with_strict_model(candidates_df, rubric_text, strictness_threshold=0.5)
end_time = time.time()

print(f"Processing took: {end_time - start_time:.4f} seconds")

# Verify Alice passed, Bob/Charlie failed, and David is Borderline
for r in results[:4]:
    print(f"Name: {r['name']} | Score: {r['score']}% | Decision: {r['decision']}")
    print(f"Coverage: {r.get('coverage', 'N/A')}% | Keywords: {r.get('keyword_match_rate', 'N/A')}%")
    print(f"Reason: {r['reason']}")
    print("-" * 20)
