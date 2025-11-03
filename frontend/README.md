# Project Management Frontend

React + Vite + TypeScript frontend for the Project Management API.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

## Features

- User authentication (login/register)
- Project management (create, view, delete)
- Document upload/download
- User invitations
- Protected routes

## Tech Stack

- React 18
- TypeScript
- Vite
- React Router
- TanStack Query
- Zustand
- Axios

## Build

```bash
npm run build
```

## Docker

```bash
docker build -t project-management-frontend .
docker run -p 80:80 project-management-frontend
```
