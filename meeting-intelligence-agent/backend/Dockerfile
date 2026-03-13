FROM python:3.11-slim

WORKDIR /app

# System dependencies (ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    gcc g++ ffmpeg libsndfile1 curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Pre-download Whisper model so first transcription is instant
RUN python -c "import whisper; whisper.load_model('base')" || true

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
