import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import { apiClient } from '../api/client'
import { Navbar } from '../components/Navbar'

export const Projects = () => {
  const [showModal, setShowModal] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.getAll
  })

  const { data: invitations } = useQuery({
    queryKey: ['invitations'],
    queryFn: async () => {
      const response = await apiClient.get('/invitations')
      return response.data
    }
  })

  const acceptInviteMutation = useMutation({
    mutationFn: async ({ token, projectId }: { token: string; projectId: number }) => {
      await apiClient.post(`/join?token=${token}&project_id=${projectId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['invitations'] })
      alert('✅ Invitation accepted!')
    },
    onError: (error: any) => {
      alert(`❌ ${error.response?.data?.detail || 'Failed to accept invitation'}`)
    }
  })

  const declineInviteMutation = useMutation({
    mutationFn: async ({ token, projectId }: { token: string; projectId: number }) => {
      await apiClient.post(`/join?token=${token}&project_id=${projectId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invitations'] })
    }
  })

  const createMutation = useMutation({
    mutationFn: projectsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowModal(false)
      setName('')
      setDescription('')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: projectsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    }
  })

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({ name, description })
  }

  return (
    <>
      <Navbar />
      <div style={styles.container}>
        <div style={styles.header}>
          <h1>Projects</h1>
          <button onClick={() => setShowModal(true)} style={styles.createBtn}>
            Create Project
          </button>
        </div>

        {invitations && invitations.length > 0 && (
          <div style={styles.invitationsSection}>
            <h2>Pending Invitations</h2>
            <div style={styles.invitationsList}>
              {invitations.map((inv: any) => (
                <div key={inv.token} style={styles.invitationCard}>
                  <div>
                    <h3>{inv.project_name}</h3>
                    <p style={styles.inviteExpiry}>
                      Expires: {new Date(inv.expires_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div style={styles.inviteActions}>
                    <button
                      onClick={() => acceptInviteMutation.mutate({ token: inv.token, projectId: inv.project_id })}
                      style={styles.acceptBtn}
                      disabled={acceptInviteMutation.isPending}
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => {
                        if (window.confirm('Decline this invitation?'))
                          declineInviteMutation.mutate({ token: inv.token, projectId: inv.project_id })
                      }}
                      style={styles.declineBtn}
                    >
                      Decline
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {isLoading ? (
          <p>Loading...</p>
        ) : (
          <div style={styles.grid}>
            {projects?.map((project) => (
              <div key={project.id} style={styles.card}>
                <h3>{project.name}</h3>
                <p style={styles.description}>{project.description}</p>
                <p style={styles.role}>Role: {project.role || 'owner'}</p>
                <div style={styles.actions}>
                  <button
                    onClick={() => navigate(`/projects/${project.id}`)}
                    style={styles.viewBtn}
                  >
                    View
                  </button>
                  {project.role === 'owner' && (
                    <button
                      onClick={() => deleteMutation.mutate(project.id)}
                      style={styles.deleteBtn}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {showModal && (
          <div style={styles.modal}>
            <div style={styles.modalContent}>
              <h2>Create Project</h2>
              <form onSubmit={handleCreate} style={styles.form}>
                <input
                  type="text"
                  placeholder="Project Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  style={styles.input}
                  required
                />
                <textarea
                  placeholder="Description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  style={styles.textarea}
                  required
                />
                <div style={styles.modalActions}>
                  <button type="submit" style={styles.submitBtn}>
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    style={styles.cancelBtn}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
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
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem'
  },
  createBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1.5rem'
  },
  card: {
    backgroundColor: '#1a1a1a',
    padding: '1.5rem',
    borderRadius: '8px',
    border: '1px solid #333'
  },
  description: {
    color: '#aaa',
    margin: '0.5rem 0'
  },
  role: {
    color: '#007bff',
    fontSize: '0.875rem',
    marginBottom: '1rem'
  },
  actions: {
    display: 'flex',
    gap: '0.5rem'
  },
  viewBtn: {
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
  },
  modal: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.8)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  modalContent: {
    backgroundColor: '#1a1a1a',
    padding: '2rem',
    borderRadius: '8px',
    width: '100%',
    maxWidth: '500px',
    border: '1px solid #333'
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
    marginTop: '1rem'
  },
  input: {
    padding: '0.75rem',
    backgroundColor: '#2a2a2a',
    border: '1px solid #444',
    borderRadius: '4px',
    color: '#fff',
    fontSize: '1rem'
  },
  textarea: {
    padding: '0.75rem',
    backgroundColor: '#2a2a2a',
    border: '1px solid #444',
    borderRadius: '4px',
    color: '#fff',
    fontSize: '1rem',
    minHeight: '100px',
    fontFamily: 'inherit'
  },
  modalActions: {
    display: 'flex',
    gap: '0.5rem'
  },
  submitBtn: {
    flex: 1,
    padding: '0.75rem',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  cancelBtn: {
    flex: 1,
    padding: '0.75rem',
    backgroundColor: '#6c757d',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  invitationsSection: {
    marginBottom: '2rem',
    padding: '1.5rem',
    backgroundColor: '#1a1a1a',
    borderRadius: '8px',
    border: '2px solid #ffc107'
  },
  invitationsList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
    marginTop: '1rem'
  },
  invitationCard: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem',
    backgroundColor: '#2a2a2a',
    borderRadius: '4px',
    border: '1px solid #ffc107'
  },
  inviteExpiry: {
    color: '#aaa',
    fontSize: '0.875rem',
    marginTop: '0.25rem'
  },
  inviteActions: {
    display: 'flex',
    gap: '0.5rem'
  },
  acceptBtn: {
    padding: '0.5rem 1rem',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  declineBtn: {
    padding: '0.5rem 1rem',
    backgroundColor: '#6c757d',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  }
}
