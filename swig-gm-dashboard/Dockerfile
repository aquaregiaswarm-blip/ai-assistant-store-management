# ============================================
# Stage 1: Build the React frontend
# ============================================
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --production=false
COPY frontend/ ./
RUN npm run build

# ============================================
# Stage 2: Python backend + serve static files
# ============================================
FROM python:3.11-slim AS production

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY --from=frontend-build /app/frontend/dist ./static

# NOTE: No DuckDB file needed — data lives in BigQuery

ENV GCP_PROJECT_ID=prj-cts-lab-vertex-sandbox
ENV BIGQUERY_DATASET=swig_operations
ENV DATA_CURRENT_DATE=2025-01-26
ENV PORT=8080

STOPSIGNAL SIGTERM
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
