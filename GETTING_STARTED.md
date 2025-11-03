# Getting Started with Your Full-Stack Project Management System

## 🎯 What You Have

A complete full-stack application with:
- ✅ React + TypeScript frontend
- ✅ FastAPI Python backend
- ✅ PostgreSQL database
- ✅ AWS S3 document storage
- ✅ JWT authentication
- ✅ Docker containerization

## 🚀 Quick Start (3 Steps)

### Step 1: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 2: Start Backend Services
```bash
docker-compose up db app localstack
```
Wait for services to be healthy (about 30 seconds)

### Step 3: Start Frontend (New Terminal)
```bash
cd frontend
npm run dev
```

### 🎉 Done!
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📋 First Time Setup Checklist

- [ ] Install Node.js 18+ (https://nodejs.org)
- [ ] Install Docker Desktop (https://docker.com)
- [ ] Clone/have the repository
- [ ] Run `cd frontend && npm install`
- [ ] Verify `.env` file exists in root directory
- [ ] Start Docker Desktop
- [ ] Run `docker-compose up db app localstack`
- [ ] Wait for "Application startup complete" message
- [ ] In new terminal: `cd frontend && npm run dev`
- [ ] Open http://localhost:3000

## 🧪 Test Your Setup

### 1. Register a User
- Go to http://localhost:3000
- Click "Register"
- Enter username, email, password
- Click "Register"

### 2. Login
- Enter your username and password
- Click "Login"
- You should be redirected to /projects

### 3. Create a Project
- Click "Create Project"
- Enter project name and description
- Click "Create"
- Project appears in the list

### 4. Upload a Document
- Click "View" on your project
- Click "Upload Files"
- Select one or more files
- Files appear in the document list

### 5. Download a Document
- Click "Download" on any document
- File downloads to your computer

### 6. Invite a User
- Create another user account (use different browser/incognito)
- In first account, enter the second user's username
- Click "Invite"
- Second user can now see the project

## 🛠️ Alternative: Windows Quick Start

Double-click `start-dev.bat` in the project root.

This will:
1. Start backend services
2. Install frontend dependencies (if needed)
3. Start frontend dev server
4. Open two terminal windows

## 🐳 Alternative: Full Docker Mode

If you prefer everything in Docker:

```bash
docker-compose up --build
```

This starts all services including the frontend.
Access at http://localhost:3000

## 📁 Project Structure Overview

```
project_management/
├── app/                   # Backend (Python/FastAPI)
├── frontend/              # Frontend (React/TypeScript)
│   ├── src/
│   │   ├── api/          # API calls
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── store/        # State management
│   │   └── types/        # TypeScript types
│   └── package.json
├── tests/                 # Backend tests
├── docker-compose.yml     # Docker services
└── README.md             # Main documentation
```

## 📚 Documentation Files

- `README.md` - Main project documentation
- `FRONTEND_SETUP.md` - Detailed frontend setup
- `FRONTEND_IMPLEMENTATION.md` - What was built
- `ARCHITECTURE.md` - System architecture
- `GETTING_STARTED.md` - This file
- `frontend/README.md` - Frontend-specific docs
- `frontend/COMPONENT_TREE.md` - Component structure

## 🔧 Common Commands

### Frontend
```bash
cd frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm install          # Install dependencies
```

### Backend
```bash
docker-compose up db app localstack    # Start backend
docker-compose down                     # Stop all services
docker-compose logs -f app              # View backend logs
```

### Database
```bash
alembic upgrade head    # Run migrations
alembic revision -m "description"  # Create migration
```

## 🌐 URLs to Bookmark

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Interactive API: http://localhost:8000/redoc

## 🎨 What You Can Do

### As a User
1. Register and login
2. Create projects
3. Upload documents (PDF, DOCX, images)
4. Download documents
5. Invite other users to projects
6. View all your projects
7. Delete projects you own
8. Delete documents

### As a Developer
1. Modify frontend components in `frontend/src/`
2. Add new API endpoints in `app/api/`
3. Create new pages in `frontend/src/pages/`
4. Add new features
5. Customize styling
6. Add tests

## 🔐 Default Credentials

There are no default credentials. You need to:
1. Register a new account
2. Use those credentials to login

## 🐛 Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend won't start
```bash
docker-compose down
docker-compose up --build
```

### Database issues
```bash
docker-compose down -v  # Remove volumes
docker-compose up
```

### Port already in use
- Frontend (3000): Change port in `frontend/vite.config.ts`
- Backend (8000): Change port in `docker-compose.yml`

### CORS errors
- Backend already has CORS enabled
- Check that backend is running on port 8000
- Verify `VITE_API_URL` in `frontend/.env`

## 📞 Getting Help

1. Check browser console (F12) for errors
2. Check backend logs: `docker-compose logs -f app`
3. Check API docs: http://localhost:8000/docs
4. Review documentation files listed above

## 🎓 Learning Path

### Beginner
1. Start the application
2. Register and login
3. Create a project
4. Upload a document
5. Explore the UI

### Intermediate
1. Read `ARCHITECTURE.md`
2. Explore `frontend/src/` files
3. Modify a component
4. Add a new feature
5. Read API documentation

### Advanced
1. Add new API endpoints
2. Implement new features
3. Add tests
4. Deploy to production
5. Optimize performance

## 🚢 Next Steps

### Immediate
- [ ] Start the application
- [ ] Create your first project
- [ ] Upload a document
- [ ] Invite a user

### Short Term
- [ ] Customize the UI colors
- [ ] Add your logo
- [ ] Deploy to a server
- [ ] Add more features

### Long Term
- [ ] Add automated tests
- [ ] Implement CI/CD
- [ ] Add monitoring
- [ ] Scale the application

## 💡 Pro Tips

1. **Use React DevTools**: Install browser extension
2. **Use API Docs**: http://localhost:8000/docs is interactive
3. **Check Network Tab**: See all API calls in browser DevTools
4. **Read Error Messages**: They usually tell you what's wrong
5. **Use TypeScript**: Let the types guide you

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Frontend loads at http://localhost:3000
- ✅ You can register a new user
- ✅ You can login
- ✅ You can create a project
- ✅ You can upload a file
- ✅ You can download a file
- ✅ No errors in browser console
- ✅ No errors in backend logs

## 📈 What's Next?

Now that you have a working full-stack application, you can:

1. **Customize**: Change colors, add features, modify UI
2. **Deploy**: Deploy to AWS, Heroku, or other platforms
3. **Extend**: Add new features like comments, tags, search
4. **Learn**: Study the code to understand how it works
5. **Share**: Show it to others, get feedback

## 🌟 Congratulations!

You now have a complete, production-ready full-stack application!

Happy coding! 🚀
