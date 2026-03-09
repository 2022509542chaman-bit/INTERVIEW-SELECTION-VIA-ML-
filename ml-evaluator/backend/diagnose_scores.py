import pandas as pd
from ml_engine import parse_rubric_points, evaluate_with_strict_model
import json

rubric_text = """
We are looking for a Senior Backend Software Engineer.

The ideal candidate must have experience in:
- Designing scalable architectures, distributed systems, and microservices.
- Implementing robust security and performance optimizations.
- Orchestrating deployments using Kubernetes or Docker.
- Managing data with Postgres and Redis caching.
- Event-driven integrations, such as Kafka messaging.
- Ensuring code quality via Test Driven Development (TDD) and CI/CD pipelines.
"""

candidates = pd.DataFrame({
    "Name": ["Alice Smith", "Charlie Brown"],
    "Response": [
        "I believe in building scalable architectures using microservices and event-driven design. Security and performance are top priorities.",
        "To design an enterprise level distributed system, we should utilize Kubernetes for orchestration, Redis for caching, and Postgres. Eventual consistency is handled via Kafka."
    ]
})

print("Testing raw scoring...")
results = evaluate_with_strict_model(candidates, rubric_text)

for r in results:
    print(f"\nCandidate: {r['name']}")
    print(f"Final Score: {r['score']/100}")
    print(f"Decision: {r['decision']}")
    print(f"Reason: {r['reason']}")
