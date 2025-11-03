# Component Tree

## Application Structure

```
App (BrowserRouter + QueryClientProvider)
│
├── Route: /login
│   └── Login
│       ├── useState (login, password)
│       ├── useAuth hook
│       └── Form
│           ├── Input (username)
│           ├── Input (password)
│           ├── Button (submit)
│           └── Link → /register
│
├── Route: /register
│   └── Register
│       ├── useState (login, email, password)
│       ├── useAuth hook
│       └── Form
│           ├── Input (username)
│           ├── Input (email)
│           ├── Input (password)
│           ├── Button (submit)
│           └── Link → /login
│
├── Route: /projects (Protected)
│   └── ProtectedRoute
│       └── Projects
│           ├── Navbar
│           │   ├── Link → /projects
│           │   ├── User display
│           │   └── Logout button
│           ├── useQuery (projects)
│           ├── useMutation (create, delete)
│           ├── useState (modal, form)
│           ├── Project Grid
│           │   └── ProjectCard (map)
│           │       ├── Project name
│           │       ├── Description
│           │       ├── Role badge
│           │       ├── View button → /projects/:id
│           │       └── Delete button (owner only)
│           └── Create Modal (conditional)
│               └── Form
│                   ├── Input (name)
│                   ├── Textarea (description)
│                   ├── Create button
│                   └── Cancel button
│
└── Route: /projects/:id (Protected)
    └── ProtectedRoute
        └── ProjectDetail
            ├── Navbar
            ├── useParams (id)
            ├── useQuery (project, documents)
            ├── useMutation (invite, upload, delete)
            ├── useState (inviteLogin)
            ├── useRef (fileInput)
            ├── Project Header
            │   ├── Project name
            │   └── Description
            ├── Invite Section
            │   └── Form
            │       ├── Input (username)
            │       └── Invite button
            └── Documents Section
                ├── Upload button (file input)
                └── Document List
                    └── DocumentCard (map)
                        ├── Filename
                        ├── Metadata (size, date)
                        ├── Download button
                        └── Delete button
```

## State Management

```
Global State (Zustand)
└── authStore
    ├── token: string | null
    ├── user: User | null
    ├── setAuth(token, user)
    └── logout()

Server State (TanStack Query)
├── ['projects']
│   ├── queryFn: projectsApi.getAll()
│   └── used in: Projects
├── ['project', projectId]
│   ├── queryFn: projectsApi.getById(id)
│   └── used in: ProjectDetail
└── ['documents', projectId]
    ├── queryFn: documentsApi.getByProject(id)
    └── used in: ProjectDetail

Mutations
├── loginMutation
│   ├── mutationFn: authApi.login()
│   └── used in: useAuth hook
├── registerMutation
│   ├── mutationFn: authApi.register()
│   └── used in: useAuth hook
├── createProjectMutation
│   ├── mutationFn: projectsApi.create()
│   └── used in: Projects
├── deleteProjectMutation
│   ├── mutationFn: projectsApi.delete()
│   └── used in: Projects
├── inviteMutation
│   ├── mutationFn: projectsApi.invite()
│   └── used in: ProjectDetail
├── uploadMutation
│   ├── mutationFn: documentsApi.upload()
│   └── used in: ProjectDetail
└── deleteDocumentMutation
    ├── mutationFn: documentsApi.delete()
    └── used in: ProjectDetail
```

## Data Flow

### Authentication Flow
```
Login Component
    ↓ (form submit)
useAuth hook
    ↓ (loginMutation)
authApi.login()
    ↓ (axios POST /login)
Backend API
    ↓ (JWT token)
authApi.getCurrentUser()
    ↓ (axios GET /auth/me)
Backend API
    ↓ (user data)
authStore.setAuth()
    ↓ (update state)
localStorage
    ↓ (persist)
Navigate to /projects
```

### Project Creation Flow
```
Projects Component
    ↓ (modal form submit)
createMutation.mutate()
    ↓ (mutation)
projectsApi.create()
    ↓ (axios POST /projects)
Backend API
    ↓ (new project)
TanStack Query
    ↓ (invalidate cache)
Re-fetch projects
    ↓ (update UI)
Projects Component
```

### Document Upload Flow
```
ProjectDetail Component
    ↓ (file input change)
uploadMutation.mutate()
    ↓ (mutation)
documentsApi.upload()
    ↓ (axios POST /project/:id/documents)
Backend API
    ↓ (upload to S3, save metadata)
TanStack Query
    ↓ (invalidate cache)
Re-fetch documents
    ↓ (update UI)
ProjectDetail Component
```

## Component Props

### ProtectedRoute
```typescript
interface Props {
  children: React.ReactNode
}
```

### Navbar
```typescript
// No props - uses global state
```

## Custom Hooks

### useAuth
```typescript
interface UseAuthReturn {
  login: (data: LoginRequest) => void
  register: (data: RegisterRequest) => void
  logout: () => void
  isLoggingIn: boolean
  isRegistering: boolean
  loginError: Error | null
  registerError: Error | null
}
```

## API Client Structure

```
apiClient (axios instance)
├── baseURL: http://localhost:8000
├── headers: { 'Content-Type': 'application/json' }
├── Request Interceptor
│   └── Add Authorization: Bearer {token}
└── Response Interceptor
    └── Handle 401 → logout & redirect

authApi
├── login(data: LoginRequest): Promise<AuthResponse>
├── register(data: RegisterRequest): Promise<User>
└── getCurrentUser(): Promise<User>

projectsApi
├── getAll(): Promise<Project[]>
├── getById(id: number): Promise<Project>
├── create(data: ProjectCreate): Promise<Project>
├── update(id: number, data: Partial<ProjectCreate>): Promise<Project>
├── delete(id: number): Promise<void>
└── invite(projectId: number, login: string): Promise<any>

documentsApi
├── getByProject(projectId: number): Promise<Document[]>
├── upload(projectId: number, files: FileList): Promise<Document[]>
├── download(documentId: number, filename: string): Promise<void>
└── delete(documentId: number): Promise<void>
```

## Routing Structure

```
/ (root)
├── Redirect to /projects
│
/login
├── Public route
└── Login component
│
/register
├── Public route
└── Register component
│
/projects
├── Protected route
└── Projects component
│
/projects/:id
├── Protected route
└── ProjectDetail component
```

## File Organization

```
src/
├── api/                    # API layer
│   ├── client.ts          # Axios instance
│   ├── auth.ts            # Auth endpoints
│   ├── projects.ts        # Project endpoints
│   └── documents.ts       # Document endpoints
│
├── components/            # Reusable components
│   ├── Navbar.tsx         # Navigation bar
│   └── ProtectedRoute.tsx # Route guard
│
├── pages/                 # Page components
│   ├── Login.tsx          # Login page
│   ├── Register.tsx       # Register page
│   ├── Projects.tsx       # Projects list
│   └── ProjectDetail.tsx  # Project details
│
├── hooks/                 # Custom hooks
│   └── useAuth.ts         # Auth hook
│
├── store/                 # State management
│   └── authStore.ts       # Zustand auth store
│
├── types/                 # TypeScript types
│   └── index.ts           # All interfaces
│
├── App.tsx                # Main app component
├── main.tsx               # Entry point
└── index.css              # Global styles
```

## Styling Approach

All components use inline styles with a consistent design system:

```typescript
const styles = {
  // Layout
  container: { maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' },
  
  // Colors
  background: '#0a0a0a',
  card: '#1a1a1a',
  input: '#2a2a2a',
  border: '#333',
  text: '#fff',
  textSecondary: '#aaa',
  
  // Buttons
  primary: '#007bff',
  success: '#28a745',
  danger: '#dc3545',
  
  // Spacing
  gap: '1rem',
  padding: '0.75rem',
  
  // Typography
  fontSize: '1rem',
  fontWeight: 'bold'
}
```

This approach keeps the bundle size minimal and styles scoped to components.
