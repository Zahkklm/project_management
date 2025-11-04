import { apiClient } from './client'
import { LoginRequest, RegisterRequest, AuthResponse, User } from '../types'

export const authApi = {
  login: async (data: LoginRequest) => {
    const response = await apiClient.post<AuthResponse>('/login', {
      login: data.login,
      password: data.password
    })
    return response.data
  },

  register: async (data: RegisterRequest) => {
    const response = await apiClient.post<User>('/auth', {
      ...data,
      repeat_password: data.password
    })
    return response.data
  }
}
