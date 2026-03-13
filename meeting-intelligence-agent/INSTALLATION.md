# Installation & Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## Quick Start with Docker

The easiest way to run the application:

```bash
# Clone repository
git clone https://github.com/seedlinglabs/meeting-intelligence-agent.git
cd meeting-intelligence-agent

# Copy environment file
cp backend/.env.example backend/.env

# Edit .env with your API keys (required):
# - OPENAI_API_KEY
# - SECRET_KEY
# - JWT_SECRET_KEY

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python scripts/create_admin.py
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

## Manual Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000

# In another terminal, start Celery worker
celery -A app.core.celery:celery_app worker --loglevel=info

# In another terminal, start Celery beat
celery -A app.core.celery:celery_app beat --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Configuration

### Required API Keys

1. **OpenAI** (required for transcription & NLP)
   - Get key: https://platform.openai.com/api-keys
   - Set in `.env`: `OPENAI_API_KEY=sk-...`

2. **Slack** (optional but recommended)
   - Create app: https://api.slack.com/apps
   - Set in `.env`: `SLACK_BOT_TOKEN=xoxb-...`

3. **Zoom** (optional)
   - Create app: https://marketplace.zoom.us/
   - Set in `.env`: `ZOOM_CLIENT_ID=...`, `ZOOM_CLIENT_SECRET=...`

4. **Linear** (optional)
   - Get API key: https://linear.app/settings/api
   - Set in `.env`: `LINEAR_API_KEY=...`

### Database Setup

```bash
# Create PostgreSQL database
createdb meeting_intel

# Run migrations
cd backend
alembic upgrade head
```

### Cloud Storage (Optional)

For production, configure S3-compatible storage:

```env
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=meeting-recordings
AWS_REGION=us-east-1
```

## Deployment

### Production with Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Kubernetes Deployment

```bash
# Apply configurations
kubectl apply -f k8s/

# Check status
kubectl get pods -n meeting-intel
```

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Check Redis is running: `redis-cli ping`
- Verify environment variables are set

### Transcription not working
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check OPENAI_API_KEY is valid
- Verify audio file format is supported (mp3, wav, m4a, etc.)

### Celery tasks not processing
- Check Redis connection
- Verify Celery worker is running: `celery -A app.core.celery:celery_app inspect active`
- Check worker logs for errors

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests  
cd frontend
npm test
```

### Code Quality

```bash
# Backend
black .
flake8 .
mypy .

# Frontend
npm run lint
```

## Support

- Documentation: https://docs.meetingintel.ai
- Issues: https://github.com/seedlinglabs/meeting-intelligence-agent/issues
- Email: support@seedlinglabs.ai
