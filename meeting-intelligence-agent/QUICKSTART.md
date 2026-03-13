# 🚀 Quick Start Guide

Get the Meeting Intelligence Agent running in **5 minutes**!

## Option 1: Docker (Recommended)

**Prerequisites**: Docker & Docker Compose installed

```bash
# 1. Navigate to project
cd meeting-intelligence-agent

# 2. Copy environment file
cp backend/.env.example backend/.env

# 3. Edit .env - Add REQUIRED keys
nano backend/.env
# Set these REQUIRED variables:
#   OPENAI_API_KEY=sk-your-key-here
#   SECRET_KEY=$(openssl rand -hex 32)
#   JWT_SECRET_KEY=$(openssl rand -hex 32)

# 4. Start all services
docker-compose up -d

# 5. Wait 30 seconds for services to initialize

# 6. Run database migrations
docker-compose exec backend alembic upgrade head

# 7. Create admin user
docker-compose exec backend python scripts/create_admin.py

# 8. Done! Access the app:
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/api/v1/docs"
```

**Login Credentials:**
- Username: `admin`
- Password: `admin123`

---

## Option 2: Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start PostgreSQL and Redis locally
# Then run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

### Celery Worker (new terminal)

```bash
cd backend
source venv/bin/activate
celery -A app.core.celery:celery_app worker --loglevel=info
```

### Frontend (new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Access app at: http://localhost:3000

---

## First Steps

1. **Login** with admin credentials
2. **Configure integrations** in Settings
   - Add Slack token for notifications
   - Connect Zoom for auto-join
   - Link Linear for action items
3. **Upload a meeting recording** (or schedule auto-capture)
4. **Watch the magic** happen:
   - Automatic transcription
   - AI-powered analysis
   - Action item extraction
   - Mention detection

### Google Meet OAuth (Real Integration)

For one-click Google OAuth from the Integrations page, set these backend env values:

```bash
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3002/integrations
```

Then in Google Cloud Console:
- Enable **Google Calendar API**
- Add `http://localhost:3002/integrations` to OAuth authorized redirect URIs
- Open the app → **Integrations** → **Google** → **Continue with Google OAuth**

---

## Test the API

```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Use token to create a meeting
curl -X POST http://localhost:8000/api/v1/meetings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting",
    "scheduled_start": "2026-03-10T10:00:00Z",
    "scheduled_end": "2026-03-10T11:00:00Z",
    "platform": "zoom"
  }'
```

---

## Troubleshooting

### "Cannot connect to database"
- Ensure PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in .env

### "Redis connection failed"
- Ensure Redis is running: `redis-cli ping`
- Check REDIS_URL in .env

### "OpenAI API error"
- Verify OPENAI_API_KEY is valid
- Check your OpenAI account has credits

### Docker containers not starting
- Check Docker is running: `docker ps`
- View logs: `docker-compose logs -f`
- Restart: `docker-compose restart`

---

## Next Steps

- 📚 Read full [README.md](README.md)
- 📖 Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- 🔧 Configure [integrations](INSTALLATION.md#configuration)
- 🎯 Review [COMPETITION_SUMMARY.md](COMPETITION_SUMMARY.md)

---

## Need Help?

- **Documentation**: Check INSTALLATION.md
- **Issues**: Open GitHub issue
- **Email**: support@seedlinglabs.ai

---

**You're all set! Start capturing meeting intelligence! 🎉**
