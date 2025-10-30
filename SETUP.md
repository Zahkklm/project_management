# Quick Setup Guide

## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Or using Poetry
poetry install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required variables:
# - DATABASE_URL
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - AWS credentials
# - S3_BUCKET_NAME
```

### 3. Start with Docker (Recommended)

```bash
# Start all services (PostgreSQL + API)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### 4. Manual Setup

```bash
# Start PostgreSQL (if not using Docker)
# Make sure PostgreSQL is running on port 5432

# Run database migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload
```

### 5. Access the Application

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 Quick Commands

```bash
# Run tests
make test
# or
pytest

# Format code
make format

# Run linters
make lint

# Create database migration
make migrate-create msg="your migration message"

# Apply migrations
make migrate
```

## 🧪 Testing the API

### 1. Create User

```bash
curl -X POST http://localhost:8000/auth \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "password123",
    "repeat_password": "password123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "password123"
  }'
```

### 3. Create Project (with token)

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My Project",
    "description": "Project description"
  }'
```

## 📦 Project Structure Overview

```
app/
├── api/              # API endpoints (auth, projects, documents)
├── core/             # Core functionality (config, database, security)
├── models/           # SQLAlchemy database models
├── schemas/          # Pydantic validation schemas
├── services/         # Business logic (S3 service)
└── main.py           # FastAPI application entry point

tests/                # Test suite
alembic/              # Database migrations
terraform/            # Infrastructure as Code
.github/workflows/    # CI/CD pipelines
```

## 🔑 Key Features Implemented

✅ JWT Authentication (1-hour expiration)
✅ User registration and login
✅ Project CRUD operations
✅ Document upload/download (S3)
✅ Role-based access control (owner/participant)
✅ Project sharing and invitations
✅ Pydantic validation for all inputs
✅ PostgreSQL with SQLAlchemy ORM
✅ Docker containerization
✅ GitHub Actions CI/CD
✅ Comprehensive test suite
✅ AWS Lambda for image processing
✅ Database migrations with Alembic

## 🛠️ Development Workflow

1. Create feature branch
2. Make changes
3. Run tests: `make test`
4. Format code: `make format`
5. Run linters: `make lint`
6. Commit and push
7. Create pull request
8. CI/CD pipeline runs automatically
9. Merge to main triggers deployment

## 📚 Additional Documentation

- [README.md](README.md) - Full project documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- API Documentation - Available at `/docs` when running

## 🐛 Troubleshooting

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs db
```

### Migration issues
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

### AWS S3 issues
- Verify AWS credentials in .env
- Check S3 bucket exists and has correct permissions
- Ensure IAM user has S3 read/write permissions
