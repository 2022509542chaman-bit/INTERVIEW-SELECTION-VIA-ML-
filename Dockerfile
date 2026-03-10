# ── Railway Dockerfile for ML Evaluator Backend (slim, CPU-only) ──
FROM python:3.9-slim AS builder

# Build deps (removed later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Install CPU-only PyTorch FIRST (~200MB vs ~3GB with CUDA)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2) Install the rest of the requirements
COPY ml-evaluator/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Final slim stage ──
FROM python:3.9-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy backend source
COPY ml-evaluator/backend/ .

# Models are ~80MB each — downloaded lazily on first /evaluate call
# This keeps the Docker image small and under Railway's 4GB limit

ENV PORT=8000
EXPOSE 8000

CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}
