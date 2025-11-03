import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useAuth } from '../hooks/useAuth'

export const Navbar = () => {
  const user = useAuthStore((state) => state.user)
  const { logout } = useAuth()

  return (
    <nav style={styles.nav}>
      <div style={styles.container}>
        <Link to="/projects" style={styles.logo}>Project Management</Link>
        <div style={styles.right}>
          <span style={styles.user}>{user?.login}</span>
          <button onClick={logout} style={styles.button}>Logout</button>
        </div>
      </div>
    </nav>
  )
}

const styles = {
  nav: {
    backgroundColor: '#1a1a1a',
    padding: '1rem 0',
    borderBottom: '1px solid #333'
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 1rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  logo: {
    color: '#fff',
    fontSize: '1.5rem',
    fontWeight: 'bold',
    textDecoration: 'none'
  },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem'
  },
  user: {
    color: '#aaa'
  },
  button: {
    padding: '0.5rem 1rem',
    backgroundColor: '#dc3545',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  }
}
