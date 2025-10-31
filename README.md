# Project Management API
[![CI/CD](https://github.com/Zahkklm/project_management/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Zahkklm/project_management/actions/workflows/ci-cd.yml)
[![Coverage](https://codecov.io/gh/Zahkklm/project_management/branch/main/graph/badge.svg)](https://codecov.io/gh/Zahkklm/project_management)

A FastAPI-based project management system with document storage, user authentication, and project collaboration features.

## Features

- **User Authentication**: JWT-based authentication with 1-hour token expiration
- **Project Management**: Create, update, delete, and share projects
- **Document Management**: Upload, download, update, and delete documents (PDF, DOCX)
- **Access Control**: Owner and participant roles with different permissions
- **AWS S3 Integration**: Secure document storage
- **PostgreSQL Database**: Robust data persistence with SQLAlchemy ORM
- **Docker Support**: Containerized application with docker-compose

## Tech Stack

- **Backend**: Python 3.10, FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **Storage**: AWS S3 (boto3)
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio
- **CI/CD**: GitHub Actions
- **Containerization**: Docker, docker-compose

## Project Structure

```
project_management/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── projects.py   # Project management endpoints
│   │   └── documents.py  # Document management endpoints
│   ├── core/             # Core functionality
│   │   ├── config.py     # Configuration settings
│   │   ├── database.py   # Database connection
│   │   └── security.py   # Security utilities
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── document.py
│   │   └── project_access.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py
│   │   ├── project.py
│   │   └── document.py
│   ├── services/         # Business logic
│   │   └── s3_service.py
│   └── main.py           # FastAPI application
├── tests/                # Test suite
├── alembic/              # Database migrations
├── .github/workflows/    # CI/CD pipelines
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- AWS Account (for S3)
- Docker & Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project_management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Setup

1. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /auth` - Create user account
- `POST /login` - Login and get JWT token

### Projects
- `POST /projects` - Create new project
- `GET /projects` - Get all accessible projects
- `GET /project/{project_id}/info` - Get project details
- `PUT /project/{project_id}/info` - Update project details
- `DELETE /project/{project_id}` - Delete project (owner only)
- `POST /project/{project_id}/invite?user={login}` - Invite user to project

### Documents
- `GET /project/{project_id}/documents` - Get all project documents
- `POST /project/{project_id}/documents` - Upload documents
- `GET /document/{document_id}` - Download document
- `PUT /document/{document_id}` - Update document
- `DELETE /document/{document_id}` - Delete document

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Linting**: Black, isort, Flake8
2. **Testing**: pytest with coverage reporting
3. **Building**: Docker image build and push to GitHub Container Registry
4. **Deployment**: Automated deployment on merge to main

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## AWS Lambda for Image Processing

Create a Lambda function for S3 event triggers:

```python
# lambda_function.py
import boto3
from PIL import Image
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Download image
    response = s3.get_object(Bucket=bucket, Key=key)
    image = Image.open(response['Body'])
    
    # Resize image
    image.thumbnail((800, 800))
    
    # Upload resized image
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    
    s3.put_object(
        Bucket=bucket,
        Key=f"resized/{key}",
        Body=buffer
    )
    
    return {'statusCode': 200}
```

## Security Best Practices

- JWT tokens expire after 1 hour
- Passwords are hashed using bcrypt
- All endpoints (except auth/login) require authentication
- Role-based access control (owner/participant)
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM

## License

MIT License
