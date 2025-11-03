import { apiClient } from './client'
import { Document } from '../types'

export const documentsApi = {
  getByProject: async (projectId: number) => {
    const response = await apiClient.get<Document[]>(`/project/${projectId}/documents`)
    return response.data
  },

  upload: async (projectId: number, files: FileList) => {
    const formData = new FormData()
    Array.from(files).forEach(file => formData.append('files', file))
    
    const response = await apiClient.post<Document[]>(
      `/project/${projectId}/documents`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    return response.data
  },

  download: async (documentId: number, filename: string) => {
    const response = await apiClient.get(`/document/${documentId}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
  },

  delete: async (documentId: number) => {
    await apiClient.delete(`/document/${documentId}`)
  }
}
