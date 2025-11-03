import { apiClient } from './client'
import { LoginRequest, RegisterRequest, AuthResponse, User } from '../types'

export const authApi = {
  login: async (data: LoginRequest) => {
    const formData = new URLSearchParams()
    formData.append('username', data.login)
    formData.append('password', data.password)
    
    const response = await apiClient.post<AuthResponse>('/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return response.data
  },

  register: async (data: RegisterRequest) => {
    const response = await apiClient.post<User>('/auth', data)
    return response.data
  },

  getCurrentUser: async () => {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  }
}
