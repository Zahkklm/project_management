import { useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi } from '../api/projects'
import { documentsApi } from '../api/documents'
import { Navbar } from '../components/Navbar'

export const ProjectDetail = () => {
  const { id } = useParams<{ id: string }>()
  const projectId = Number(id)
  const [inviteLogin, setInviteLogin] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()

  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.getById(projectId)
  })

  const { data: documents } = useQuery({
    queryKey: ['documents', projectId],
    queryFn: () => documentsApi.getByProject(projectId)
  })

  const inviteMutation = useMutation({
    mutationFn: (login: string) => projectsApi.invite(projectId, login),
    onSuccess: () => {
      setInviteLogin('')
      alert('✅ User invited successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to invite user'
      alert(`❌ ${message}`)
    }
  })

  const uploadMutation = useMutation({
    mutationFn: (files: FileList) => documentsApi.upload(projectId, files),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', projectId] })
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  })

  const deleteMutation = useMutation({
    mutationFn: documentsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', projectId] })
    }
  })

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadMutation.mutate(e.target.files)
    }
  }

  const handleInvite = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inviteLogin.trim()) {
      alert('❌ Please enter a username')
      return
    }
    inviteMutation.mutate(inviteLogin.trim())
  }

  return (
    <>
      <Navbar />
      <div style={styles.container}>
        <div style={styles.header}>
          <div>
            <h1>{project?.name}</h1>
            <p style={styles.description}>{project?.description}</p>
          </div>
        </div>

        <div style={styles.section}>
          <h2>Invite User</h2>
          <form onSubmit={handleInvite} style={styles.inviteForm}>
            <input
              type="text"
              placeholder="Username"
              value={inviteLogin}
              onChange={(e) => setInviteLogin(e.target.value)}
              style={styles.input}
            />
            <button type="submit" style={styles.inviteBtn}>
              Invite
            </button>
          </form>
        </div>

        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <h2>Documents</h2>
            <label style={styles.uploadBtn}>
              Upload Files
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </label>
          </div>

          <div style={styles.docList}>
            {documents?.map((doc) => (
              <div key={doc.id} style={styles.docCard}>
                <div>
                  <p style={styles.filename}>{doc.filename}</p>
                  <p style={styles.meta}>
                    {(doc.size / 1024).toFixed(2)} KB • {new Date(doc.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
                <div style={styles.docActions}>
                  <button
                    onClick={() => documentsApi.download(doc.id, doc.filename)}
                    style={styles.downloadBtn}
                  >
                    Download
                  </button>
                  <button
                    onClick={() => {
                      if (window.confirm(`Delete "${doc.filename}"?`))
                        deleteMutation.mutate(doc.id)
                    }}
                    style={styles.deleteBtn}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem 1rem'
  },
  header: {
    marginBottom: '2rem'
  },
  description: {
    color: '#aaa',
    marginTop: '0.5rem'
  },
  section: {
    marginBottom: '2rem',
    backgroundColor: '#1a1a1a',
    padding: '1.5rem',
    borderRadius: '8px',
    border: '1px solid #333'
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem'
  },
  inviteForm: {
    display: 'flex',
    gap: '0.5rem',
    marginTop: '1rem'
  },
  input: {
    flex: 1,
    padding: '0.75rem',
    backgroundColor: '#2a2a2a',
    border: '1px solid #444',
    borderRadius: '4px',
    color: '#fff',
    fontSize: '1rem'
  },
  inviteBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  uploadBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  docList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.75rem'
  },
  docCard: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem',
    backgroundColor: '#2a2a2a',
    borderRadius: '4px',
    border: '1px solid #444'
  },
  filename: {
    fontWeight: 'bold',
    marginBottom: '0.25rem'
  },
  meta: {
    color: '#aaa',
    fontSize: '0.875rem'
  },
  docActions: {
    display: 'flex',
    gap: '0.5rem'
  },
  downloadBtn: {
    padding: '0.5rem 1rem',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  deleteBtn: {
    padding: '0.5rem 1rem',
    backgroundColor: '#dc3545',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  }
}
