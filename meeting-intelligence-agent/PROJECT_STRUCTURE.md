# Project Structure

```
meeting-intelligence-agent/
├── README.md                          # Main project documentation
├── INSTALLATION.md                    # Setup and installation guide
├── API_DOCUMENTATION.md               # Complete API reference
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT License
├── docker-compose.yml                 # Docker orchestration
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml                  # CI/CD pipeline
│
├── backend/                           # FastAPI Backend
│   ├── Dockerfile                     # Backend container
│   ├── requirements.txt               # Python dependencies
│   ├── alembic.ini                    # Database migration config
│   ├── .env.example                   # Environment template
│   │
│   ├── alembic/                       # Database migrations
│   │   ├── env.py                     # Alembic environment
│   │   └── versions/                  # Migration scripts
│   │
│   └── app/
│       ├── main.py                    # Application entry point
│       │
│       ├── api/                       # API endpoints
│       │   └── v1/
│       │       ├── router.py          # Main API router
│       │       └── endpoints/
│       │           ├── auth.py        # Authentication
│       │           ├── meetings.py    # Meeting management
│       │           ├── action_items.py# Action item tracking
│       │           ├── mentions.py    # Mention detection
│       │           ├── analytics.py   # Analytics & insights
│       │           ├── integrations.py# External integrations
│       │           ├── transcripts.py # Transcript access
│       │           └── users.py       # User management
│       │
│       ├── core/                      # Core configurations
│       │   ├── config.py             # Settings management
│       │   ├── database.py           # Database connection
│       │   ├── redis.py              # Redis cache
│       │   ├── security.py           # Auth & security
│       │   ├── logging.py            # Logging setup
│       │   └── celery.py             # Background tasks
│       │
│       ├── models/                    # Database models
│       │   ├── __init__.py
│       │   ├── user.py               # User model
│       │   ├── meeting.py            # Meeting model
│       │   ├── transcript.py         # Transcript model
│       │   ├── action_item.py        # Action item model
│       │   └── mention.py            # Mention & decision models
│       │
│       ├── services/                  # Business logic
│       │   ├── ai/
│       │   │   ├── transcription.py  # Whisper AI transcription
│       │   │   └── nlp.py            # NLP analysis (GPT-4)
│       │   │
│       │   └── integrations/
│       │       ├── slack.py          # Slack integration
│       │       ├── zoom.py           # Zoom integration
│       │       └── linear.py         # Linear integration
│       │
│       ├── tasks/                     # Celery background tasks
│       │   └── meeting_processor.py  # Meeting processing pipeline
│       │
│       └── middleware/                # Custom middleware
│           ├── request_id.py         # Request ID tracking
│           └── rate_limit.py         # Rate limiting
│
├── frontend/                          # React Frontend
│   ├── Dockerfile                     # Frontend container
│   ├── package.json                   # Node dependencies
│   ├── vite.config.ts                # Vite configuration
│   ├── tailwind.config.js            # Tailwind CSS config
│   ├── index.html                     # HTML entry point
│   │
│   └── src/
│       ├── main.tsx                   # React entry point
│       ├── App.tsx                    # Main App component
│       ├── index.css                  # Global styles
│       │
│       ├── components/                # Reusable components
│       │   └── Layout.tsx            # App layout with sidebar
│       │
│       └── pages/                     # Page components
│           ├── Dashboard.tsx          # Main dashboard
│           ├── Meetings.tsx           # Meeting list
│           ├── MeetingDetail.tsx      # Meeting details
│           ├── ActionItems.tsx        # Action item tracker
│           ├── Mentions.tsx           # User mentions
│           ├── Analytics.tsx          # Analytics dashboard
│           ├── Settings.tsx           # User settings
│           └── Login.tsx              # Authentication
│
└── uploads/                           # Local file storage
    └── recordings/                    # Meeting recordings
```

## Key Components

### Backend Architecture

**FastAPI Application**
- Async/await for high performance
- OpenAPI/Swagger documentation
- Dependency injection
- Background task processing

**Database Layer**
- PostgreSQL with SQLAlchemy ORM
- Async database operations
- Migration system with Alembic
- Full-text search capabilities

**AI Services**
- **Transcription**: OpenAI Whisper (large-v3)
- **Speaker Diarization**: Pyannote.audio
- **NLP Analysis**: GPT-4 Turbo
- **Embeddings**: OpenAI text-embedding-3-large
- **Sentiment Analysis**: Custom BERT model

**Integration Services**
- **Slack**: Real-time notifications
- **Zoom**: Meeting bot & recording access
- **Linear**: Task creation & sync
- **Google Calendar**: Meeting scheduling
- **Microsoft Teams**: Enterprise support

**Background Processing**
- Celery workers for async tasks
- Redis for task queue & caching
- Scheduled reminders with Celery Beat
- Scalable worker architecture

### Frontend Architecture

**React + TypeScript**
- Functional components with hooks
- Type-safe development
- Vite for fast dev server
- Hot module replacement

**State Management**
- React Query for server state
- Zustand for client state
- Optimistic updates
- Automatic cache invalidation

**UI Components**
- Tailwind CSS for styling
- Lucide React for icons
- shadcn/ui component library
- Responsive design

**Features**
- Dashboard with real-time stats
- Meeting list & detail views
- Action item tracker
- Mention notifications
- Analytics & insights
- Settings & integrations

### DevOps

**Docker**
- Multi-service orchestration
- Development & production configs
- Volume persistence
- Health checks

**CI/CD**
- Automated testing
- Code quality checks
- Docker image building
- Deployment automation

**Monitoring**
- Prometheus metrics
- Sentry error tracking
- Structured logging
- Request tracing

## Data Flow

1. **Meeting Recording** → Upload or Auto-capture
2. **Transcription** → Whisper AI + Speaker Diarization
3. **NLP Analysis** → GPT-4 extracts insights
4. **Database Storage** → PostgreSQL with full-text search
5. **Real-time Notifications** → Slack/Email alerts
6. **Action Item Sync** → Linear/Jira/Asana
7. **User Access** → React dashboard

## Security

- **Authentication**: JWT tokens with refresh
- **Authorization**: Role-based access control
- **Encryption**: AES-256 for recordings
- **Rate Limiting**: Per-user and per-IP
- **CORS**: Configurable origins
- **Input Validation**: Pydantic schemas
- **SQL Injection**: Prevented by ORM
- **XSS**: React auto-escaping

## Scalability

- **Horizontal Scaling**: Stateless API servers
- **Database**: Read replicas, connection pooling
- **Cache Layer**: Redis for hot data
- **Task Queue**: Multiple Celery workers
- **File Storage**: S3-compatible object storage
- **CDN**: Static asset delivery
- **Load Balancing**: Nginx/HAProxy ready
