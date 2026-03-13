# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Use Token
```http
GET /meetings/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Meetings

### List Meetings
```http
GET /meetings/?skip=0&limit=50&status=completed
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Product Roadmap Review",
    "description": "Q2 planning session",
    "platform": "zoom",
    "scheduled_start": "2026-03-05T10:00:00Z",
    "scheduled_end": "2026-03-05T11:00:00Z",
    "status": "completed",
    "summary": "Discussed Q2 priorities...",
    "created_at": "2026-03-04T15:00:00Z"
  }
]
```

### Get Meeting Details
```http
GET /meetings/{meeting_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "title": "Product Roadmap Review",
  "description": "Q2 planning session",
  "platform": "zoom",
  "scheduled_start": "2026-03-05T10:00:00Z",
  "scheduled_end": "2026-03-05T11:00:00Z",
  "actual_start": "2026-03-05T10:03:00Z",
  "actual_end": "2026-03-05T10:58:00Z",
  "status": "completed",
  "transcription_status": "completed",
  "analysis_status": "completed",
  "summary": "Discussed Q2 priorities...",
  "key_decisions": [...],
  "discussion_topics": [...],
  "sentiment_score": 0.7,
  "meeting_quality_score": 85.5
}
```

### Create Meeting
```http
POST /meetings/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Sprint Planning",
  "description": "Weekly sprint planning",
  "platform": "zoom",
  "scheduled_start": "2026-03-10T14:00:00Z",
  "scheduled_end": "2026-03-10T15:30:00Z",
  "attendee_ids": ["uuid1", "uuid2"],
  "tags": ["engineering", "sprint"]
}
```

### Upload Recording
```http
POST /meetings/{meeting_id}/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@meeting_recording.mp4
```

## Action Items

### List Action Items
```http
GET /action-items/?status=open&priority=high
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Complete API documentation",
    "description": "Document all endpoints",
    "meeting_id": "uuid",
    "owner_id": "uuid",
    "status": "open",
    "priority": "high",
    "due_date": "2026-03-10T00:00:00Z",
    "completed_at": null,
    "created_at": "2026-03-05T10:00:00Z"
  }
]
```

### Create Action Item
```http
POST /action-items/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Review PR #123",
  "description": "Code review for new feature",
  "meeting_id": "uuid",
  "owner_id": "uuid",
  "due_date": "2026-03-08T00:00:00Z",
  "priority": "high",
  "category": "development"
}
```

### Update Action Item
```http
PATCH /action-items/{item_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "in_progress",
  "priority": "urgent"
}
```

### Complete Action Item
```http
POST /action-items/{item_id}/complete
Authorization: Bearer <token>
```

## Mentions

### List User Mentions
```http
GET /mentions/?unread=true
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "meeting_id": "uuid",
    "user_id": "uuid",
    "mention_type": "action_assignment",
    "mentioned_text": "Sarah, can you handle the API integration?",
    "context": "...",
    "relevance_score": 95.0,
    "is_action_item": true,
    "notification_read": false,
    "created_at": "2026-03-05T10:15:00Z"
  }
]
```

## Analytics

### Get Dashboard Analytics
```http
GET /analytics/dashboard
Authorization: Bearer <token>
```

**Response:**
```json
{
  "meeting_stats": {
    "total_meetings": 127,
    "total_hours": 254.5,
    "avg_duration_minutes": 45,
    "this_week_count": 8,
    "this_month_count": 32
  },
  "action_item_stats": {
    "total": 156,
    "completed": 144,
    "in_progress": 8,
    "overdue": 4,
    "completion_rate": 92.3
  },
  "time_saved_hours": 109.4,
  "decision_velocity": 2.3
}
```

### Get Meeting Efficiency
```http
GET /analytics/meeting-efficiency
Authorization: Bearer <token>
```

## Integrations

### List Integrations
```http
GET /integrations/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "name": "Slack",
    "type": "communication",
    "status": "connected",
    "enabled": true
  },
  {
    "name": "Linear",
    "type": "project_management",
    "status": "connected",
    "enabled": true
  }
]
```

### Connect Slack
```http
POST /integrations/slack/connect
Authorization: Bearer <token>
```

Returns OAuth URL for user to authorize.

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error message",
  "request_id": "uuid"
}
```

### Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content (Delete)
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

## Rate Limits

- 60 requests per minute per IP
- 1000 requests per hour per authenticated user

Headers included in response:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1678012345
```

## Webhooks

Configure webhooks to receive real-time updates:

### Available Events

- `meeting.completed` - Meeting processing finished
- `action_item.created` - New action item
- `action_item.completed` - Action item completed
- `mention.detected` - User mentioned
- `decision.made` - Decision recorded

### Webhook Payload Example

```json
{
  "event": "meeting.completed",
  "timestamp": "2026-03-05T10:00:00Z",
  "data": {
    "meeting_id": "uuid",
    "title": "Product Review",
    "summary": "...",
    "action_items_count": 5
  }
}
```

## Interactive Documentation

Full interactive API documentation available at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`
