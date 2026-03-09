import pandas as pd
from ml_engine import evaluate_with_strict_model

# Dummy data for test
data = {
    "Name": ["Alice", "Bob"],
    "Response": [
        "I have 5 years of experience in Python, specifically with FastAPI and machine learning pipelines. I've built recommendation engines.",
        "I like creating simple HTML pages. Occasionally I use some Excel for basic analysis but I am not very familiar with coding."
    ]
}

candidates_df = pd.DataFrame(data)
rubric_text = "Looking for a software engineer with strong Python skills, experience in building APIs and machine learning background."

print("Running deep learning evaluator...")
results = evaluate_with_strict_model(candidates_df, rubric_text)

for r in results:
    print(f"\nName: {r['name']} | Score: {r['score']}% | Decision: {r['decision']}")
    print(f"Reason: {r['reason']}")
    print(f"Coverage: {r['coverage']}% | Keywords: {r['keyword_match_rate']}%")
