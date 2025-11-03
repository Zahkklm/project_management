export interface User {
  id: number
  login: string
  email: string
}

export interface Project {
  id: number
  name: string
  description: string
  owner_id: number
  created_at: string
  role?: string
}

export interface Document {
  id: number
  filename: string
  s3_key: string
  content_type: string
  size: number
  project_id: number
  uploaded_by: number
  uploaded_at: string
}

export interface LoginRequest {
  login: string
  password: string
}

export interface RegisterRequest {
  login: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface ProjectCreate {
  name: string
  description: string
}
