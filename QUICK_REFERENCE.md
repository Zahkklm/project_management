# Quick Reference Guide

## 🚀 Start Commands

### Development (Recommended)
```bash
# Terminal 1
docker-compose up db app localstack

# Terminal 2
cd frontend && npm run dev
```

### Windows Quick Start
```bash
start-dev.bat
```

### Full Docker
```bash
docker-compose up --build
```

## 🌐 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Interactive API | http://localhost:8000/redoc |

## 📁 Key Files

### Frontend
```
frontend/
├── src/
│   ├── api/              # API integration
│   │   ├── client.ts     # Axios + JWT
│   │   ├── auth.ts       # Auth endpoints
│   │   ├── projects.ts   # Project endpoints
│   │   └── documents.ts  # Document endpoints
│   ├── components/       # Reusable components
│   │   ├── Navbar.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/            # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Projects.tsx
│   │   └── ProjectDetail.tsx
│   ├── hooks/
│   │   └── useAuth.ts    # Auth hook
│   ├── store/
│   │   └── authStore.ts  # Zustand store
│   ├── types/
│   │   └── index.ts      # TypeScript types
│   ├── App.tsx           # Main app
│   └── main.tsx          # Entry point
└── package.json
```

### Backend
```
app/
├── api/                  # Endpoints
│   ├── auth.py
│   ├── projects.py
│   └── documents.py
├── core/                 # Config
├── models/               # Database models
├── schemas/              # Pydantic schemas
└── services/             # Business logic
```

## 🎯 Common Tasks

### Create New User
1. Go to http://localhost:3000
2. Click "Register"
3. Fill form and submit

### Create Project
1. Login
2. Click "Create Project"
3. Enter name and description
4. Click "Create"

### Upload Document
1. Open project
2. Click "Upload Files"
3. Select files
4. Files upload automatically

### Invite User
1. Open project
2. Enter username in invite form
3. Click "Invite"

## 🛠️ Development

### Add New Page
1. Create file in `frontend/src/pages/`
2. Add route in `frontend/src/App.tsx`
3. Add navigation link if needed

### Add New API Endpoint
1. Add function in `frontend/src/api/`
2. Use in component with TanStack Query
3. Handle loading/error states

### Modify Styles
- All styles are inline in components
- Modify the `styles` object in each component
- Consistent design tokens used throughout

## 🔧 Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Backend won't start
```bash
docker-compose down
docker-compose up --build
```

### Clear everything
```bash
docker-compose down -v
cd frontend && rm -rf node_modules
npm install
cd .. && docker-compose up --build
```

### Port conflicts
- Frontend: Change port in `vite.config.ts`
- Backend: Change port in `docker-compose.yml`

## 📦 Dependencies

### Install Frontend
```bash
cd frontend
npm install
```

### Update Dependencies
```bash
cd frontend
npm update
```

### Add New Dependency
```bash
cd frontend
npm install package-name
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app

# Rebuild containers
docker-compose up --build

# Remove volumes
docker-compose down -v
```

## 🔐 Environment Variables

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=...
SECRET_KEY=...
```

## 📊 API Endpoints

### Auth
- POST `/auth` - Register
- POST `/login` - Login
- GET `/auth/me` - Current user

### Projects
- GET `/projects` - List all
- POST `/projects` - Create
- GET `/project/{id}/info` - Get details
- PUT `/project/{id}/info` - Update
- DELETE `/project/{id}` - Delete
- POST `/project/{id}/invite?user={login}` - Invite

### Documents
- GET `/project/{id}/documents` - List
- POST `/project/{id}/documents` - Upload
- GET `/document/{id}` - Download
- DELETE `/document/{id}` - Delete

## 🎨 UI Components

### Navbar
- Logo/title
- User display
- Logout button

### ProtectedRoute
- Checks authentication
- Redirects to login if needed

### Login/Register
- Form inputs
- Submit button
- Link to other page

### Projects
- Project grid
- Create button
- Project cards with actions

### ProjectDetail
- Project info
- Invite form
- Document list
- Upload button

## 🔄 State Management

### Auth State (Zustand)
```typescript
const { token, user, setAuth, logout } = useAuthStore()
```

### Server State (TanStack Query)
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['projects'],
  queryFn: projectsApi.getAll
})
```

### Mutations
```typescript
const mutation = useMutation({
  mutationFn: projectsApi.create,
  onSuccess: () => {
    queryClient.invalidateQueries(['projects'])
  }
})
```

## 📚 Documentation

| File | Description |
|------|-------------|
| GETTING_STARTED.md | Quick start guide |
| FRONTEND_SETUP.md | Detailed setup |
| FRONTEND_IMPLEMENTATION.md | What was built |
| ARCHITECTURE.md | System architecture |
| IMPLEMENTATION_COMPLETE.md | Summary |
| QUICK_REFERENCE.md | This file |

## 🎯 Testing Checklist

- [ ] Register new user
- [ ] Login
- [ ] Create project
- [ ] Upload document
- [ ] Download document
- [ ] Invite user
- [ ] Delete document
- [ ] Delete project
- [ ] Logout
- [ ] Try accessing /projects without login

## 💡 Tips

1. Use React DevTools browser extension
2. Check Network tab in browser DevTools
3. Use API docs at /docs for testing
4. Read error messages carefully
5. Check both frontend and backend logs

## 🚀 Deployment

### Build Frontend
```bash
cd frontend
npm run build
# Output: frontend/dist/
```

### Deploy with Docker
```bash
docker build -t pm-frontend ./frontend
docker run -p 80:80 pm-frontend
```

### Environment for Production
```env
VITE_API_URL=https://your-api-domain.com
```

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| CORS error | Check backend is on port 8000 |
| 401 error | Clear localStorage and login again |
| Upload fails | Check S3/LocalStack is running |
| Port in use | Change port in config |
| npm errors | Delete node_modules and reinstall |

## ⚡ Performance

- Vite HMR: Instant updates
- TanStack Query: Request caching
- Code splitting: Faster loads
- Tree shaking: Smaller bundles
- Gzip: Compressed assets

## 🎉 Success Indicators

✅ Frontend loads at localhost:3000
✅ Can register and login
✅ Can create projects
✅ Can upload files
✅ No console errors
✅ No backend errors

---

**Need more help?** Check the documentation files listed above!
