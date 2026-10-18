# ==============================================================================
# Dockerfile: Container configuration for Docker / Koyeb / Fly.io / Cloud Run
# ==============================================================================

# 1. Base image with lightweight Python 3.12
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependencies first for efficient layer caching
COPY requirements.txt .

# 4. Install dependencies without caching unnecessary wheel files
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Default environment variables for Layer 4 (OS Env)
ENV APP_PORT=8144
ENV APP_WORKERS=11

# 7. Document the default listening port
EXPOSE 8000

# 8. Start Uvicorn, dynamically respecting $PORT if provided by the host
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
