#!/usr/bin/env python3
import os


def generate_frontend_dockerfile():
    content = """# Stage 1: Development dependencies & Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production
FROM node:18-alpine AS runner

WORKDIR /app

# Copy necessary files from builder
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# Set environment to production
ENV NODE_ENV=production

# Expose the port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
"""
    with open("frontend/Dockerfile", "w") as f:
        f.write(content)
    print("✅ Generated frontend/Dockerfile")


def generate_backend_dockerfile():
    content = """FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    gcc \\
    python3-dev \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    with open("backend/Dockerfile", "w") as f:
        f.write(content)
    print("✅ Generated backend/Dockerfile")


def generate_docker_compose():
    content = """version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017
      - AWS_ACCESS_KEY_ID=minio
      - AWS_SECRET_ACCESS_KEY=minio123
      - AWS_REGION=us-east-1
      - S3_BUCKET_NAME=family-photos
      - FRONTEND_URL=http://localhost:3000
    depends_on:
      - mongodb
      - qdrant
      - minio
    networks:
      - app-network

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - app-network

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - app-network

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9090:9090"
    volumes:
      - minio_data:/data
    environment:
      - MINIO_ROOT_USER=minio
      - MINIO_ROOT_PASSWORD=minio123
    command: server /data --console-address ":9090"
    networks:
      - app-network

  createbuckets:
    image: minio/mc
    depends_on:
      - minio
    entrypoint: >
      /bin/sh -c "
      sleep 5;
      mc alias set myminio http://minio:9000 minio minio123;
      mc mb myminio/family-photos;
      mc anonymous set public myminio/family-photos;
      exit 0;
      "
    networks:
      - app-network

volumes:
  mongodb_data:
  qdrant_data:
  minio_data:

networks:
  app-network:
    driver: bridge
"""
    with open("docker-compose.yml", "w") as f:
        f.write(content)
    print("✅ Generated docker-compose.yml")


def main():
    # Create directories if they don't exist
    os.makedirs("frontend", exist_ok=True)
    os.makedirs("backend", exist_ok=True)

    # Generate all configuration files
    generate_frontend_dockerfile()
    generate_backend_dockerfile()
    generate_docker_compose()

    print("\n🎉 All Docker configuration files have been generated!")
    print("\nTo start the application:")
    print("1. Make sure you have Docker installed")
    print("2. Run: docker-compose up --build")
    print("\nTo stop the application:")
    print("Run: docker-compose down")


if __name__ == "__main__":
    main()
