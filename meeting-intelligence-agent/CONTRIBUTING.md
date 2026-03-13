# Contributing to Meeting Intelligence Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/meeting-intelligence-agent.git
   cd meeting-intelligence-agent
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Set up development environment**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

   # Frontend
   cd frontend
   npm install
   ```

## Development Workflow

### Backend

1. **Make changes** in appropriate files
2. **Add tests** for new functionality
3. **Run tests**
   ```bash
   pytest tests/ -v
   ```

4. **Format code**
   ```bash
   black .
   isort .
   ```

5. **Check linting**
   ```bash
   flake8 .
   mypy .
   ```

### Frontend

1. **Make changes** in appropriate files
2. **Run development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

4. **Run linter**
   ```bash
   npm run lint
   ```

## Commit Messages

Follow conventional commit format:

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add meeting summary endpoint

Implements POST /api/v1/meetings/{id}/summary endpoint
that generates AI-powered meeting summaries.

Closes #123
```

```
fix(transcription): handle empty audio files

Added validation to check audio file size before
processing to prevent crashes.
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md**
5. **Create Pull Request** with clear description

### PR Title Format
```
[Type] Brief description

Example: [Feature] Add real-time mention notifications
```

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

## Testing Guidelines

### Backend Tests

Location: `backend/tests/`

```python
# test_meetings.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_meeting(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/meetings/",
        json={
            "title": "Test Meeting",
            "scheduled_start": "2026-03-10T10:00:00Z",
            "scheduled_end": "2026-03-10T11:00:00Z",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Meeting"
```

### Frontend Tests

Location: `frontend/src/__tests__/`

```typescript
// Dashboard.test.tsx
import { render, screen } from '@testing-library/react'
import Dashboard from '../pages/Dashboard'

test('renders dashboard title', () => {
  render(<Dashboard />)
  expect(screen.getByText('Dashboard')).toBeInTheDocument()
})
```

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions/classes

```python
from typing import List, Optional

def process_meeting(
    meeting_id: str,
    options: Optional[Dict] = None,
) -> List[ActionItem]:
    """
    Process meeting recording and extract action items.
    
    Args:
        meeting_id: Unique meeting identifier
        options: Optional processing configuration
    
    Returns:
        List of extracted action items
    """
    # Implementation
    pass
```

### TypeScript (Frontend)

- Use functional components with hooks
- Use TypeScript for type safety
- Follow Airbnb style guide

```typescript
interface Meeting {
  id: string
  title: string
  status: 'scheduled' | 'in_progress' | 'completed'
}

const MeetingCard: React.FC<{ meeting: Meeting }> = ({ meeting }) => {
  return (
    <div className="meeting-card">
      <h3>{meeting.title}</h3>
      <span>{meeting.status}</span>
    </div>
  )
}
```

## Documentation

- Update README.md for user-facing changes
- Update API_DOCUMENTATION.md for API changes
- Add inline comments for complex logic
- Update INSTALLATION.md for setup changes

## Feature Requests

Submit feature requests via GitHub Issues with:

1. **Clear title**
2. **Problem description**
3. **Proposed solution**
4. **Alternative solutions considered**
5. **Additional context**

## Bug Reports

Submit bug reports via GitHub Issues with:

1. **Clear title**
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Screenshots (if applicable)**
6. **Environment details**
   - OS
   - Python/Node version
   - Browser (for frontend)

## Questions?

- Open a GitHub Discussion
- Email: dev@seedlinglabs.ai
- Join our Discord: [link]

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
