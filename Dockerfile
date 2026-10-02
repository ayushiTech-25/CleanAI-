# Stage 1: Dependency builder stage
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install dependencies in user folder to easily copy
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final lightweight runtime stage
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy site-packages from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Set environment paths
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

# Container healthcheck definition
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 -c "import requests; requests.get('http://localhost:8501/_stcore/health')" || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
