# ⚛️ React Integration Guide - Vira Services Backend

This guide shows you how to connect your React application to the Vira Services backend, step by step.

## 🎯 Overview
- **Backend:** Running on `http://localhost:8080`
- **Frontend:** Your React app (typically on `http://localhost:3000`)
- **Communication:** REST API calls with JWT authentication

## 📋 Prerequisites

### 1. Ensure Backend is Running
```bash
# Start the backend first
cd vira-services
.\mvnw.cmd spring-boot:run
```
Verify at: `http://localhost:8080/actuator/health`

### 2. Have a React App Ready
```bash
# If you don't have one, create it
npx create-react-app my-frontend
cd my-frontend
npm start
```

## 🔧 Step 1: Install Required Packages

```bash
# Navigate to your React project
cd my-frontend

# Install HTTP client for API calls
npm install axios

# Optional: For better development experience
npm install @types/node  # If using TypeScript
```

## 📁 Step 2: Create API Service Layer

### Create `src/services/api.js`
```javascript
import axios from 'axios';

// Base configuration
const API_BASE_URL = 'http://localhost:8080/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests automatically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh automatically
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refreshToken,
          });
          
          const { accessToken } = response.data.data;
          localStorage.setItem('accessToken', accessToken);
          
          // Retry original request
          error.config.headers.Authorization = `Bearer ${accessToken}`;
          return api.request(error.config);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

## 🔐 Step 3: Create Authentication Service

### Create `src/services/authService.js`
```javascript
import api from './api';

export const authService = {
  // Register new user
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // Login user
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    const { data } = response.data;
    
    // Store tokens
    localStorage.setItem('accessToken', data.accessToken);
    localStorage.setItem('refreshToken', data.refreshToken);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  },

  // Logout user
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    }
  },

  // Get current user
  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('accessToken');
  },
};
```

## 📂 Step 4: Create Portfolio Service

### Create `src/services/portfolioService.js`
```javascript
import api from './api';

export const portfolioService = {
  // Get all projects
  getProjects: async (page = 0, size = 10) => {
    const response = await api.get(`/portfolio/projects?page=${page}&size=${size}`);
    return response.data;
  },

  // Get project by ID
  getProject: async (id) => {
    const response = await api.get(`/portfolio/projects/${id}`);
    return response.data;
  },

  // Create new project
  createProject: async (projectData) => {
    const response = await api.post('/portfolio/projects', projectData);
    return response.data;
  },

  // Update project
  updateProject: async (id, projectData) => {
    const response = await api.put(`/portfolio/projects/${id}`, projectData);
    return response.data;
  },

  // Delete project
  deleteProject: async (id) => {
    const response = await api.delete(`/portfolio/projects/${id}`);
    return response.data;
  },

  // Get featured projects
  getFeaturedProjects: async () => {
    const response = await api.get('/portfolio/projects/featured');
    return response.data;
  },

  // Search projects
  searchProjects: async (query, page = 0, size = 10) => {
    const response = await api.get(`/portfolio/projects/search?q=${query}&page=${page}&size=${size}`);
    return response.data;
  },
};
```

## ⚛️ Step 5: Create React Components

### Create `src/components/Login.js`
```javascript
import React, { useState } from 'react';
import { authService } from '../services/authService';

const Login = ({ onLoginSuccess }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await authService.login(formData);
      console.log('Login successful:', result);
      onLoginSuccess(result.user);
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px' }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
            style={{ width: '100%', padding: '10px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
            style={{ width: '100%', padding: '10px' }}
          />
        </div>
        {error && (
          <div style={{ color: 'red', marginBottom: '15px' }}>{error}</div>
        )}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

### Create `src/components/ProjectList.js`
```javascript
import React, { useState, useEffect } from 'react';
import { portfolioService } from '../services/portfolioService';

const ProjectList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await portfolioService.getProjects();
      setProjects(response.data.content); // Spring Boot pagination format
    } catch (err) {
      setError('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await portfolioService.deleteProject(id);
        fetchProjects(); // Refresh list
      } catch (err) {
        alert('Failed to delete project');
      }
    }
  };

  if (loading) return <div>Loading projects...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>My Projects</h2>
      {projects.length === 0 ? (
        <p>No projects found. Create your first project!</p>
      ) : (
        <div style={{ display: 'grid', gap: '20px' }}>
          {projects.map((project) => (
            <div
              key={project.id}
              style={{
                border: '1px solid #ddd',
                padding: '15px',
                borderRadius: '8px',
              }}
            >
              <h3>{project.title}</h3>
              <p>{project.description}</p>
              <div>
                <strong>Technologies:</strong>{' '}
                {project.technologies?.join(', ') || 'None'}
              </div>
              <div>
                <strong>Status:</strong> {project.status}
              </div>
              {project.link && (
                <div>
                  <strong>Live URL:</strong>{' '}
                  <a href={project.link} target="_blank" rel="noopener noreferrer">
                    View Project
                  </a>
                </div>
              )}
              <div style={{ marginTop: '10px' }}>
                <button
                  onClick={() => handleDelete(project.id)}
                  style={{
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    padding: '5px 10px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectList;
```

## 🔗 Step 6: Update Your Main App Component

### Update `src/App.js`
```javascript
import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import ProjectList from './components/ProjectList';
import { authService } from './services/authService';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const currentUser = authService.getCurrentUser();
    if (currentUser && authService.isAuthenticated()) {
      setUser(currentUser);
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="App">
      {user ? (
        <div>
          <header style={{ padding: '20px', borderBottom: '1px solid #ddd' }}>
            <h1>Vira Services Dashboard</h1>
            <div>
              Welcome, {user.username}!{' '}
              <button onClick={handleLogout}>Logout</button>
            </div>
          </header>
          <ProjectList />
        </div>
      ) : (
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;
```

## 🌐 Step 7: Handle CORS (If Needed)

If you get CORS errors, the backend is already configured to allow `http://localhost:3000`. If you're running React on a different port, update the backend configuration:

### In `src/main/resources/application-dev.yml`:
```yaml
cors:
  allowed-origins: 
    - http://localhost:3000
    - http://localhost:3001  # Add your React port here
```

## 🧪 Step 8: Test the Integration

### 1. Start Both Applications
```bash
# Terminal 1: Start backend
cd vira-services
.\mvnw.cmd spring-boot:run

# Terminal 2: Start React app
cd my-frontend
npm start
```

### 2. Test the Flow
1. Open `http://localhost:3000`
2. You should see a login form
3. Register a new user first (or use Swagger UI at `http://localhost:8080/swagger-ui/index.html`):
   ```bash
   curl -X POST http://localhost:8080/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"demo","email":"demo@example.com","password":"password123"}'
   ```
4. Login with: `username: demo`, `password: password123`
5. You should see the dashboard with empty projects list

**Note**: If you get authentication errors, create a fresh user with a different username as H2 in-memory database may reset between restarts.

## 📱 Step 9: Add Environment Variables (Production Ready)

### Create `.env` file in React project root:
```env
REACT_APP_API_URL=http://localhost:8080/api
```

### Update `src/services/api.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';
```

## 🛠️ Troubleshooting

### Issue 1: CORS Errors
**Solution:** Ensure backend CORS is configured for your React app port

### Issue 2: "Network Error"
**Solution:** Check if backend is running on correct port

### Issue 3: Token Not Persisting
**Solution:** Check browser localStorage in DevTools

### Issue 4: 401 Unauthorized
**Solution:** Check if token is being sent in headers

## 📚 Common API Patterns

### Error Handling
```javascript
try {
  const response = await api.get('/portfolio/projects');
  // Handle success
} catch (error) {
  if (error.response?.status === 401) {
    // Handle authentication error
  } else if (error.response?.status === 403) {
    // Handle permission error
  } else {
    // Handle other errors
    console.error('API Error:', error.response?.data?.message);
  }
}
```

### Loading States
```javascript
const [loading, setLoading] = useState(false);

const handleSubmit = async () => {
  setLoading(true);
  try {
    await someApiCall();
  } finally {
    setLoading(false);
  }
};
```

---

**🎉 Success!** Your React app is now connected to the Vira Services backend! 