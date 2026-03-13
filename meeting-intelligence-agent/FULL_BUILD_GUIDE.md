# 🚀 Full Build & Deployment Guide

## Current Status ✅

### Backend (FULLY OPERATIONAL)
- ✅ FastAPI server running on `http://localhost:8000`
- ✅ All endpoints fixed (async/sync issues resolved)
- ✅ Authentication working (JWT tokens)
- ✅ Database operational (SQLite)
- ✅ Action items, meetings, analytics endpoints ready

**Test commands:**
```bash
# Login (get JWT token)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'username=admin&password=admin123'

# List meetings (requires token)
curl http://localhost:8000/api/v1/meetings/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Admin credentials:**
- Username: `admin`
- Password: `admin123`

---

## Frontend (React + Vite + TypeScript)

### Prerequisites
You need **Node.js 18+** and **npm** installed.

#### Install Node.js (macOS)
```bash
# Option 1: Using Homebrew (if available)
brew install node

# Option 2: Download from nodejs.org
# https://nodejs.org/ (LTS version recommended)

# Option 3: Using nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

This starts the frontend on `http://localhost:5173`

---

## Complete Full-Stack Startup

### Terminal 1 - Backend
```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm install  # (first time only)
npm run dev
```

Visit: `http://localhost:5173`

---

## Production Build

### Backend
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
npm run preview  # or use a static server
```

---

## API Documentation

**Base URL:** `http://localhost:8000/api/v1`

### Authentication

**POST** `/auth/login`
- Request: `username`, `password`
- Response: `access_token`, `refresh_token`, `token_type`

**POST** `/auth/register`
- Request: `email`, `username`, `full_name`, `password`
- Response: User object

**GET** `/auth/me`
- Headers: `Authorization: Bearer <token>`
- Response: Current user object

### Meetings

**GET** `/meetings/` - List meetings (paginated)
**POST** `/meetings/` - Create meeting
**GET** `/meetings/{id}` - Get meeting details
**POST** `/meetings/{id}/upload` - Upload meeting recording
**DELETE** `/meetings/{id}` - Delete meeting

### Action Items

**GET** `/action_items/` - List action items
**POST** `/action_items/` - Create action item
**GET** `/action_items/{id}` - Get item details
**PATCH** `/action_items/{id}` - Update item
**POST** `/action_items/{id}/complete` - Mark complete

### Analytics

**GET** `/analytics/dashboard` - Get dashboard metrics
**GET** `/analytics/meeting-efficiency` - Meeting efficiency data

---

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///app.db
SQLALCHEMY_ECHO=False
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Kill process on port 5173
lsof -ti :5173 | xargs kill -9
```

### Frontend Can't Connect to Backend
- Ensure backend is running on 8000
- Check browser console for CORS errors
- Verify `VITE_API_BASE_URL` is correct

### Database Errors
```bash
# Reset database
rm -f backend/app.db
# Restart backend to recreate tables
```

---

## Docker Deployment (Optional)

```bash
docker-compose up -d
```

Visit: `http://localhost`

---

## Features Included

✅ User authentication (JWT)
✅ Meeting management (CRUD)
✅ Meeting recording upload
✅ Action item tracking
✅ Analytics dashboard
✅ Real-time updates (Socket.io ready)
✅ Responsive UI (Tailwind CSS)
✅ Type-safe frontend (TypeScript)

---

**Ready to launch?** Start with Terminal 1 (Backend) then Terminal 2 (Frontend)!
