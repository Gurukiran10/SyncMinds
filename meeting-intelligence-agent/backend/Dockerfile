FROM python:3.11-slim

WORKDIR /app

# System dependencies (ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    gcc g++ ffmpeg libsndfile1 curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from minimal requirements
COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application
COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
