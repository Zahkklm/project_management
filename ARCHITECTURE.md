# System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│                    http://localhost:3000                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   React Frontend                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Pages: Login, Register, Projects, ProjectDetail     │   │
│  │  Components: Navbar, ProtectedRoute                  │   │
│  │  State: Zustand (auth), TanStack Query (server)      │   │
│  │  Routing: React Router v6                            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Axios + JWT
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                            │
│                  http://localhost:8000                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Endpoints:                                           │   │
│  │  - POST /auth (register)                             │   │
│  │  - POST /login (JWT token)                           │   │
│  │  - GET/POST /projects                                │   │
│  │  - GET/PUT/DELETE /project/{id}                      │   │
│  │  - POST /project/{id}/invite                         │   │
│  │  - GET/POST/DELETE /documents                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────┬──────────────────────────────┬────────────────────┘
          │                              │
          │                              │
          ▼                              ▼
┌─────────────────────┐      ┌──────────────────────┐
│   PostgreSQL DB     │      │    AWS S3 / Local    │
│   localhost:5432    │      │   Document Storage   │
│                     │      │    localhost:4566    │
│  Tables:            │      │                      │
│  - users            │      │  Buckets:            │
│  - projects         │      │  - documents         │
│  - documents        │      │  - images            │
│  - project_access   │      │                      │
│  - invite_tokens    │      │                      │
└─────────────────────┘      └──────────────────────┘
```

## Data Flow

### Authentication Flow
```
1. User enters credentials → Frontend
2. Frontend sends POST /login → Backend
3. Backend validates → PostgreSQL
4. Backend generates JWT token → Frontend
5. Frontend stores token → localStorage
6. All subsequent requests include JWT in Authorization header
```

### Project Management Flow
```
1. User creates project → Frontend
2. Frontend sends POST /projects with JWT → Backend
3. Backend validates JWT → Creates project → PostgreSQL
4. Backend returns project data → Frontend
5. Frontend updates UI with TanStack Query cache
```

### Document Upload Flow
```
1. User selects files → Frontend
2. Frontend sends multipart/form-data → Backend
3. Backend validates → Uploads to S3 → Stores metadata in PostgreSQL
4. Backend returns document info → Frontend
5. Frontend refreshes document list
```

## Technology Stack

### Frontend Layer
- **React 18**: Component-based UI
- **TypeScript**: Type safety
- **Vite**: Fast build tool
- **React Router**: Client-side routing
- **TanStack Query**: Server state & caching
- **Zustand**: Client state (auth)
- **Axios**: HTTP client with interceptors

### Backend Layer
- **FastAPI**: High-performance Python framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation
- **JWT**: Token-based authentication
- **Boto3**: AWS S3 integration

### Data Layer
- **PostgreSQL**: Relational database
- **AWS S3**: Object storage for documents
- **LocalStack**: Local AWS emulation

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Frontend web server (production)

## Security

### Authentication
- JWT tokens with 1-hour expiration
- Passwords hashed with bcrypt
- Token stored in localStorage
- Auto-redirect on 401 errors

### Authorization
- Role-based access (owner/participant)
- Project-level permissions
- Document access tied to project access

### API Security
- CORS enabled for frontend origin
- JWT validation on protected endpoints
- SQL injection prevention via ORM
- File type validation on uploads

## Deployment

### Development
```bash
# Terminal 1: Backend
docker-compose up db app localstack

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Production
```bash
# Build and deploy all services
docker-compose up --build -d
```

### AWS Deployment
- **ECS Fargate**: Backend containers
- **S3 + CloudFront**: Frontend static hosting
- **RDS PostgreSQL**: Managed database
- **S3**: Document storage
- **ALB**: Load balancing
- **Lambda**: Image processing

## API Endpoints

### Authentication
- `POST /auth` - Register user
- `POST /login` - Login (returns JWT)

### Projects
- `GET /projects` - List all accessible projects
- `POST /projects` - Create project
- `GET /project/{id}/info` - Get project details
- `PUT /project/{id}/info` - Update project
- `DELETE /project/{id}` - Delete project (owner only)
- `POST /project/{id}/invite?user={login}` - Invite user

### Documents
- `GET /project/{id}/documents` - List project documents
- `POST /project/{id}/documents` - Upload documents
- `GET /document/{id}` - Download document
- `DELETE /document/{id}` - Delete document

## State Management

### Frontend State
```
┌─────────────────────────────────────┐
│         Zustand (Auth Store)        │
│  - token: string | null             │
│  - user: User | null                │
│  - setAuth(), logout()              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    TanStack Query (Server State)    │
│  - projects: useQuery               │
│  - documents: useQuery              │
│  - mutations: create, update, delete│
│  - automatic cache invalidation     │
└─────────────────────────────────────┘
```

### Backend State
```
┌─────────────────────────────────────┐
│         PostgreSQL Database         │
│  - Persistent storage               │
│  - ACID transactions                │
│  - Foreign key constraints          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│            AWS S3 Storage           │
│  - Document files                   │
│  - Versioning enabled               │
│  - Presigned URLs for downloads     │
└─────────────────────────────────────┘
```

## Performance Optimizations

### Frontend
- Code splitting with React Router
- TanStack Query caching (reduces API calls)
- Optimistic updates for better UX
- Lazy loading of components

### Backend
- Database connection pooling
- Async/await for I/O operations
- Indexed database queries
- S3 multipart uploads for large files

### Infrastructure
- Docker multi-stage builds
- Nginx gzip compression
- CDN for static assets (production)
- Database query optimization

## Monitoring & Logging

### Development
- Browser DevTools for frontend debugging
- FastAPI automatic API docs at `/docs`
- Docker logs: `docker-compose logs -f`

### Production
- CloudWatch for AWS services
- Application logs to CloudWatch Logs
- Error tracking with Sentry (optional)
- Performance monitoring with New Relic (optional)
