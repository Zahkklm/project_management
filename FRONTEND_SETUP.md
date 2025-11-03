# Frontend Setup Guide

## Quick Start

### Option 1: Development Mode (Recommended for development)

1. **Install frontend dependencies:**
```bash
cd frontend
npm install
```

2. **Start the backend:**
```bash
cd ..
docker-compose up db app localstack
```

3. **Start the frontend (in a new terminal):**
```bash
cd frontend
npm run dev
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Full Docker Setup

1. **Start all services:**
```bash
docker-compose up --build
```

2. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client & endpoints
│   │   ├── client.ts     # Axios instance with interceptors
│   │   ├── auth.ts       # Authentication API
│   │   ├── projects.ts   # Projects API
│   │   └── documents.ts  # Documents API
│   ├── components/       # Reusable components
│   │   ├── Navbar.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/            # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Projects.tsx
│   │   └── ProjectDetail.tsx
│   ├── hooks/            # Custom React hooks
│   │   └── useAuth.ts
│   ├── store/            # State management
│   │   └── authStore.ts  # Zustand auth store
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── Dockerfile
└── nginx.conf
```

## Features Implemented

### Authentication
- ✅ User registration
- ✅ User login with JWT
- ✅ Token storage in localStorage
- ✅ Auto-redirect on 401 errors
- ✅ Protected routes

### Projects
- ✅ List all projects
- ✅ Create new project
- ✅ View project details
- ✅ Delete project (owner only)
- ✅ Invite users to project

### Documents
- ✅ Upload multiple files
- ✅ List project documents
- ✅ Download documents
- ✅ Delete documents
- ✅ Display file metadata (size, date)

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`. All API calls include:
- JWT token in Authorization header
- Automatic token refresh handling
- Error handling with user feedback

## Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
```

## Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
```

## Tech Stack

- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool & dev server
- **React Router**: Client-side routing
- **TanStack Query**: Server state management
- **Zustand**: Client state management
- **Axios**: HTTP client

## Usage Flow

1. **Register/Login:**
   - Navigate to `/login` or `/register`
   - Create account or login with credentials
   - JWT token stored automatically

2. **View Projects:**
   - After login, redirected to `/projects`
   - See all projects you own or have access to
   - Create new projects with the "Create Project" button

3. **Manage Project:**
   - Click "View" on any project
   - Invite users by username
   - Upload documents (drag & drop or click)
   - Download or delete documents

4. **Logout:**
   - Click "Logout" in the navbar
   - Token cleared, redirected to login

## Troubleshooting

### CORS Issues
The backend already has CORS enabled for all origins. If you still face issues:
- Check that backend is running on port 8000
- Verify `VITE_API_URL` in `.env`

### Authentication Errors
- Clear localStorage: `localStorage.clear()`
- Check backend logs for JWT errors
- Verify token expiration (1 hour default)

### File Upload Issues
- Check file size limits in backend
- Verify S3/LocalStack is running
- Check browser console for errors

## Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
```

### Deploy with Docker
```bash
docker build -t project-management-frontend ./frontend
docker run -p 80:80 project-management-frontend
```

### Environment Variables for Production
Update `.env` with production API URL:
```env
VITE_API_URL=https://your-api-domain.com
```

## Next Steps

Potential enhancements:
- Add loading skeletons
- Implement toast notifications
- Add file preview (PDF viewer)
- Implement drag & drop for file upload
- Add project search/filter
- Add user profile page
- Implement real-time updates with WebSockets
- Add dark/light theme toggle
- Implement pagination for large lists
