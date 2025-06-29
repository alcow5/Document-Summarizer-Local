# Multi-stage Dockerfile for Privacy-Focused AI Document Summarizer
# Includes Ollama, backend, and frontend in a single container

FROM node:18-alpine as frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM python:3.10-slim as backend-builder

# Build backend
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    python3 \
    python3-pip \
    nodejs \
    npm \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create app directory
WORKDIR /app

# Copy backend
COPY --from=backend-builder /app/backend /app/backend
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy frontend build
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Copy configuration
COPY backend/config.yaml /app/backend/
COPY database/schema.sql /app/database/

# Create entrypoint script
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash

# Start Ollama in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 5

# Pull the required model
ollama pull llama3:8b

# Start the backend
cd /app/backend
python3 -m app.main &
BACKEND_PID=$!

# Start a simple HTTP server for frontend
cd /app/frontend/build
python3 -m http.server 3050 &
FRONTEND_PID=$!

# Wait for any process to exit
wait $OLLAMA_PID $BACKEND_PID $FRONTEND_PID
EOF

RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 3050 8050 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8050/health || exit 1

# Start services
CMD ["/app/start.sh"] 