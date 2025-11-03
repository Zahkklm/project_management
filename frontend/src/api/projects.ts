import { apiClient } from './client'
import { Project, ProjectCreate } from '../types'

export const projectsApi = {
  getAll: async () => {
    const response = await apiClient.get<Project[]>('/projects')
    return response.data
  },

  getById: async (id: number) => {
    const response = await apiClient.get<Project>(`/project/${id}/info`)
    return response.data
  },

  create: async (data: ProjectCreate) => {
    const response = await apiClient.post<Project>('/projects', data)
    return response.data
  },

  update: async (id: number, data: Partial<ProjectCreate>) => {
    const response = await apiClient.put<Project>(`/project/${id}/info`, data)
    return response.data
  },

  delete: async (id: number) => {
    await apiClient.delete(`/project/${id}`)
  },

  invite: async (projectId: number, login: string) => {
    const response = await apiClient.post(`/project/${projectId}/invite?user=${login}`)
    return response.data
  }
}
