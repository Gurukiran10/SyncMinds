# 🚀 Real Build & Launch Guide

This guide shows you how to build and actually **run** the Meeting Intelligence Agent application in your local development environment.

---

## ⚡ Quick Start (5 minutes)

### Option 1: Python Auto-Launch (Recommended)

```bash
cd /Applications/vs\ codee/meeting-intelligence-agent
python3 launch.py
```

That's it! The script will:
- ✅ Check Python installation
- ✅ Install missing dependencies
- ✅ Setup environment configuration
- ✅ Initialize database
- ✅ Start the server

### Option 2: Shell Script (macOS/Linux)

```bash
cd /Applications/vs\ codee/meeting-intelligence-agent
chmod +x run.sh
./run.sh
```

### Option 3: Batch Script (Windows)

```cmd
cd "C:\your\path\meeting-intelligence-agent"
run.bat
```

### Option 4: Manual Launch

```bash
cd /Applications/vs\ codee/meeting-intelligence-agent/backend

# Install dependencies
python3 -m pip install fastapi uvicorn sqlalchemy pydantic python-dotenv

# Create .env file
cat > .env << 'EOF'
SECRET_KEY=your-secret-key-minimum-32-characters-long
JWT_SECRET_KEY=your-jwt-secret-key-minimum-32-chars
DATABASE_URL=sqlite:///./app.db
ENVIRONMENT=development
DEBUG=True
ADMIN_USER_PASSWORD=admin123
DEMO_USER_PASSWORD=demo123
EOF

# Start server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📍 Access the Application

Once the server starts, you'll see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

### Available URLs:

| Resource | URL |
|----------|-----|
| **Frontend** | http://localhost:3000 |
| **API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |
| **Root** | http://localhost:8000/ |

### Default Credentials:

```
Admin Account:
  Email: admin@meetingintel.ai
  Password: admin123

Demo Account:
  Email: demo@meetingintel.ai
  Password: demo123
```

---

## 🔧 Project Structure

```
meeting-intelligence-agent/
├── backend/                 # Python FastAPI application
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── core/           # Core services (database, auth, etc.)
│   │   ├── models/         # Database models
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── tasks/          # Celery tasks
│   │   └── middleware/     # Middleware
│   ├── .env                # Environment configuration (created on first run)
│   ├── app.db             # SQLite database (created on first run)
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React application (add later)
│
├── launch.py              # 🟢 MAIN LAUNCHER (Python)
├── run.sh                 # 🟢 LAUNCHER (macOS/Linux)
├── run.bat                # 🟢 LAUNCHER (Windows)
├── docker-compose.yml     # Docker setup
│
├── README.md              # Main documentation
├── QUICKSTART.md          # Quick start guide
└── PROJECT_OVERVIEW.md    # Complete overview
```

---

## 🛠️ Detailed Setup Steps

### Step 1: Prerequisites

**Check Python Version:**
```bash
python3 --version
# Should be 3.9 or higher
```

**Install Python if needed:**
- macOS: `brew install python3`
- Windows: Download from https://www.python.org
- Linux: `sudo apt-get install python3 python3-pip`

### Step 2: Install Core Dependencies

```bash
cd /Applications/vs\ codee/meeting-intelligence-agent/backend

python3 -m pip install --upgrade pip
python3 -m pip install fastapi uvicorn sqlalchemy pydantic python-dotenv aiosqlite
```

### Step 3: Configure Environment

Create `.env` file in `backend/` directory:

```bash
cat > backend/.env << 'EOF'
# Application
APP_NAME=Meeting Intelligence Agent
ENVIRONMENT=development
DEBUG=True

# Security (Change in production!)
SECRET_KEY=dev-secret-key-minimum-32-characters-this-is-a-sample-key
JWT_SECRET_KEY=dev-jwt-key-minimum-32-characters-this-is-a-sample-key

# Database
DATABASE_URL=sqlite:///./app.db

# Redis (optional, app works without it)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# API Keys (optional, add when ready)
# OPENAI_API_KEY=sk-...
# SLACK_BOT_TOKEN=xoxb-...

# Users
ADMIN_USER_EMAIL=admin@meetingintel.ai
ADMIN_USER_PASSWORD=admin123
DEMO_USER_EMAIL=demo@meetingintel.ai
DEMO_USER_PASSWORD=demo123
EOF
```

### Step 4: Start the Application

```bash
cd /Applications/vs\ codee/meeting-intelligence-agent/backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
```

### Step 5: Test the API

```bash
# In another terminal
curl http://localhost:8000/
# Returns: {"name":"Meeting Intelligence Agent","version":"1.0.0","status":"operational","environment":"development"}

curl http://localhost:8000/health
# Returns: {"status":"healthy","database":"connected","redis":"connected"}

curl http://localhost:8000/docs
# Opens API documentation in browser
```

---

## 📚 API Testing

### Using Swagger UI (Browser)

1. Open http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters
4. Click "Execute"

### Using Python Requests

```bash
python3 << 'EOF'
import requests

# Test health endpoint
response = requests.get("http://localhost:8000/health")
print("Health Check:", response.json())

# Test root endpoint
response = requests.get("http://localhost:8000/")
print("Root:", response.json())
EOF
```

### Using cURL

```bash
# Root endpoint
curl -X GET http://localhost:8000/

# Health check
curl -X GET http://localhost:8000/health

# Get API schema
curl -X GET http://localhost:8000/openapi.json
```

---

## 🐛 Troubleshooting

### Issue: "Command not found: python3"

**Solution:** Python is not installed or not in PATH
```bash
# macOS
brew install python3

# Windows
# Download from https://www.python.org and ensure "Add to PATH" is checked

# Linux
sudo apt-get install python3 python3-pip
```

### Issue: "Port 8000 already in use"

**Solution:** Change the port
```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Or kill the process using port 8000:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:** Install dependencies
```bash
python3 -m pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
```

### Issue: "No such file or directory: './app.db'"

**Solution:** Database will be created on first run. The error is just a warning and can be ignored.

### Issue: "Redis connection failed"

**Solution:** This is optional. The app works without Redis. To enable Redis:
```bash
# macOS
brew install redis
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:latest

# Option: Just ignore the warning and continue
```

---

## 🎯 Next Steps

### Get More Features:

1. **Install All Dependencies** (for AI features):
```bash
python3 -m pip install openai pyannote.audio librosa faster-whisper slack-sdk
```

2. **Add OpenAI API Key:**
```bash
# Edit backend/.env
# Add: OPENAI_API_KEY=sk-your-actual-key-here
```

3. **Run Frontend** (separate terminal):
```bash
cd /Applications/vs\ codee/meeting-intelligence-agent/frontend
npm install
npm run dev
```

### Deploy with Docker:

```bash
cd /Applications/vs\ codee/meeting-intelligence-agent
docker-compose up -d
```

---

## 📊 Application Files Generated

Once you run the application:

```
backend/
├── app.db              # SQLite database (auto-created)
├── uploads/            # Recording uploads directory (auto-created)
├── .env                # Environment config (auto-created)
└── app.log            # Application logs (auto-created)
```

---

## ✅ Verification Checklist

After starting the application, verify everything works:

- [ ] Server starts without errors
- [ ] http://localhost:8000 returns JSON response
- [ ] http://localhost:8000/health returns healthy status
- [ ] http://localhost:8000/docs loads API documentation
- [ ] Can see API endpoints listed

---

## 💡 Development Tips

### Enable File Watching

The `--reload` flag auto-restarts the server when you modify code:
```bash
python3 -m uvicorn app.main:app --reload
```

### View Logs in Real-Time

```bash
# All logs
tail -f app.log

# Just errors
grep ERROR app.log
```

### Access Database

```bash
# SQLite CLI
sqlite3 app.db

# Show tables
.tables

# Query users
SELECT * FROM user;

# Exit
.exit
```

---

## 📞 Support

If you encounter issues:

1. Check [QUICKSTART.md](QUICKSTART.md) for 5-minute setup
2. Review [README.md](README.md) for full documentation
3. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
4. Check error messages in terminal output

---

## 🎉 Success!

Your Meeting Intelligence Agent is now **running in real-time**!

```
✅ API Server: http://localhost:8000
✅ API Docs: http://localhost:8000/docs
✅ Status: Operational
✅ Ready for: Testing, Development, Competition
```

Press **Ctrl+C** to stop the server anytime.

**Happy development! 🚀**
