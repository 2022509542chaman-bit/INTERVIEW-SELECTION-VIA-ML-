# ── Stage 1: Build Frontend ──
FROM node:18-slim AS frontend-builder
WORKDIR /build
# Copy only package files first for caching
COPY ml-evaluator/package*.json ./
RUN npm install
# Copy the rest of the frontend/root source
COPY ml-evaluator/ ./
RUN npm run build

# ── Stage 2: Build Backend ──
FROM python:3.9-slim AS backend-builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# Install CPU-only PyTorch (large dependency, cached early)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY ml-evaluator/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 3: Final Production Stage ──
FROM python:3.9-slim
WORKDIR /app
# Copy installed packages from builder
COPY --from=backend-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend source into a subfolder to match local path logic
COPY ml-evaluator/backend/ ./backend/
# Copy built frontend output
COPY --from=frontend-builder /build/dist ./frontend/dist

ENV PORT=8000
EXPOSE 8000

# Run uvicorn pointing to the backend subfolder
CMD python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
