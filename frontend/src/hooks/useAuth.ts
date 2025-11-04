import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import { LoginRequest, RegisterRequest } from '../types'

export const useAuth = () => {
  const navigate = useNavigate()
  const { setAuth, logout } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      console.log('Login successful, token received:', data.access_token?.substring(0, 20))
      setAuth(data.access_token, { id: 0, login: '', email: '' })
      console.log('Token stored, navigating to /projects')
      navigate('/projects', { replace: true })
    },
    onError: (error) => {
      console.error('Login failed:', error)
    }
  })

  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      navigate('/login')
    }
  })

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return {
    login: (data: LoginRequest) => loginMutation.mutate(data),
    register: (data: RegisterRequest) => registerMutation.mutate(data),
    logout: handleLogout,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error
  }
}
