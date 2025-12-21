import { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:8001'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Check if user is logged in on mount
  useEffect(() => {
    checkSession()
  }, [])

  const checkSession = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/bff/me`, {
        credentials: 'include', // 🔑 This sends HttpOnly cookies
      })
      
      if (response.ok) {
        const data = await response.json()
        setUser(data)
      } else {
        setUser(null)
      }
    } catch (err) {
      setError('Failed to connect to backend. Is it running on port 8001?')
      console.error('Session check failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = () => {
    // 🚀 BFF Pattern: Just redirect to backend
    // Backend handles entire OAuth flow
    // No tokens in JavaScript!
    window.location.href = `${API_BASE}/bff/auth/login`
  }

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/bff/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
      setUser(null)
    } catch (err) {
      setError('Logout failed')
      console.error('Logout failed:', err)
    }
  }

  const handleTestMockOAuth = () => {
    // For demo: use mock OAuth provider
    window.location.href = `${API_BASE}/bff/mock/authorize?client_id=demo&redirect_uri=${encodeURIComponent(API_BASE + '/bff/auth/callback')}&state=test123`
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Checking session...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🔐 BFF Auth Demo</h1>
        <p>Backend-for-Frontend OAuth Pattern</p>
        <span className="badge">Secure Session-Based Auth</span>
      </div>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className={`status-box ${user ? 'authenticated' : 'unauthenticated'}`}>
        <div className="status-label">
          {user ? '✅ Authenticated' : '🔒 Not Authenticated'}
        </div>
        
        {user ? (
          <div className="user-info">
            <div className="user-info-item">
              <label>User ID:</label>
              <span>{user.id}</span>
            </div>
            <div className="user-info-item">
              <label>Email:</label>
              <span>{user.email}</span>
            </div>
            <div className="user-info-item">
              <label>Name:</label>
              <span>{user.name}</span>
            </div>
          </div>
        ) : (
          <p style={{ marginTop: '12px', color: '#666' }}>
            Click "Login" to start the OAuth flow. Backend handles everything!
          </p>
        )}
      </div>

      <div className="button-group">
        {user ? (
          <>
            <button className="btn-secondary" onClick={checkSession}>
              🔄 Refresh Session
            </button>
            <button className="btn-danger" onClick={handleLogout}>
              🚪 Logout
            </button>
          </>
        ) : (
          <>
            <button className="btn-primary" onClick={handleLogin}>
              🔑 Login (Real OAuth)
            </button>
            <button className="btn-secondary" onClick={handleTestMockOAuth}>
              🧪 Test Mock OAuth
            </button>
          </>
        )}
      </div>

      <div className="info-section">
        <h3>🎯 How BFF Pattern Works</h3>
        <ul>
          <li><strong>Frontend:</strong> No tokens stored! Just redirects to backend</li>
          <li><strong>Backend:</strong> Handles OAuth, stores tokens server-side</li>
          <li><strong>Session:</strong> HttpOnly cookie (can't be accessed by JavaScript)</li>
          <li><strong>Security:</strong> Protected from XSS attacks</li>
          <li><strong>Simplicity:</strong> Frontend only needs <code>credentials: 'include'</code></li>
        </ul>

        <h3 style={{ marginTop: '24px' }}>� Try the Main Application</h3>
        <div style={{ marginTop: '16px' }}>
          <a 
            href="http://localhost:5173" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              display: 'inline-block',
              padding: '12px 24px',
              background: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              transition: 'all 0.2s'
            }}
          >
            Open LLM Council App →
          </a>
          <p style={{ marginTop: '12px', color: '#666', fontSize: '14px' }}>
            The main application uses JWT authentication. Start it with:<br/>
            <code style={{ background: '#f3f4f6', padding: '4px 8px', borderRadius: '4px' }}>
              cd frontend && npm run dev
            </code>
          </p>
        </div>

        <h3 style={{ marginTop: '24px' }}>�📝 Frontend Code</h3>
        <div className="code-block">
          {`// Login: Just redirect
window.location.href = 'http://localhost:8001/bff/auth/login'

// API calls: Include credentials
fetch('http://localhost:8001/bff/me', {
  credentials: 'include' // Sends HttpOnly cookie
})

// That's it! No token management needed.`}
        </div>

        <h3 style={{ marginTop: '24px' }}>🔗 Backend Endpoints</h3>
        <ul style={{ fontSize: '14px' }}>
          <li><code>GET /bff/auth/login</code> - Start OAuth flow</li>
          <li><code>GET /bff/auth/callback</code> - Handle OAuth redirect</li>
          <li><code>POST /bff/auth/logout</code> - Clear session</li>
          <li><code>GET /bff/me</code> - Get current user</li>
          <li><code>GET /bff/mock/*</code> - Mock OAuth for testing</li>
        </ul>
      </div>
    </div>
  )
}

export default App
