# ── Railway Dockerfile for ML Evaluator Backend ──
FROM python:3.9-slim

# System deps for numpy / scipy / pandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Set working directory to the backend folder
WORKDIR /app

# Copy only requirements first (Docker layer cache)
COPY ml-evaluator/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the ML models during build so they're cached in the image
RUN python -c "\
from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('all-MiniLM-L6-v2'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2'); \
print('Models cached ✓')"

# Copy backend source
COPY ml-evaluator/backend/ .

# Railway injects $PORT at runtime
ENV PORT=8000
EXPOSE 8000

CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}
