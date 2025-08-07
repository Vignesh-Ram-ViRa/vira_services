# React Frontend Integration Guide

## 🎯 **Complete React Integration with Vira Services Backend**

This guide shows you exactly how to integrate your React applications with the Vira Services Spring Boot backend. Includes authentication, API calls, error handling, and best practices.

## 📋 **Prerequisites**

- ✅ Vira Services backend running (locally or deployed)
- ✅ React application set up
- ✅ Basic knowledge of React hooks and async/await

## 🔧 **Step 1: Setup API Configuration**

### 1.1 Create API Configuration File
Create `src/config/api.js`:

```javascript
// src/config/api.js
const API_CONFIG = {
  // Local development
  LOCAL: 'http://localhost:8080',
  
  // Production (replace with your Railway URL)
  PRODUCTION: 'https://your-app-name.railway.app',
  
  // Current environment
  BASE_URL: process.env.NODE_ENV === 'production' 
    ? 'https://your-app-name.railway.app'
    : 'http://localhost:8080'
};

export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    REGISTER: `${API_CONFIG.BASE_URL}/api/auth/register`,
    LOGIN: `${API_CONFIG.BASE_URL}/api/auth/login`,
    REFRESH: `${API_CONFIG.BASE_URL}/api/auth/refresh`,
    LOGOUT: `${API_CONFIG.BASE_URL}/api/auth/logout`,
    ME: `${API_CONFIG.BASE_URL}/api/auth/me`
  },
  
  // Portfolio
  PORTFOLIO: {
    PROJECTS: `${API_CONFIG.BASE_URL}/api/portfolio/projects`,
    PROJECT_BY_ID: (id) => `${API_CONFIG.BASE_URL}/api/portfolio/projects/${id}`,
    FEATURED: `${API_CONFIG.BASE_URL}/api/portfolio/projects/featured`,
    BY_CATEGORY: (category) => `${API_CONFIG.BASE_URL}/api/portfolio/projects/by-category/${category}`
  }
};

export default API_CONFIG;
```

### 1.2 Create Environment Variables
Create `.env` and `.env.production`:

```bash
# .env (local development)
REACT_APP_API_BASE_URL=http://localhost:8080

# .env.production (production build)
REACT_APP_API_BASE_URL=https://your-app-name.railway.app
```

## 🔐 **Step 2: Authentication Service**

### 2.1 Create Authentication Context
Create `src/context/AuthContext.js`:

```javascript
// src/context/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Check if user is logged in on app start
  useEffect(() => {
    if (token) {
      getCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const apiCall = async (url, options = {}) => {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token expired or invalid
          logout();
          throw new Error('Authentication required');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await apiCall(API_ENDPOINTS.AUTH.REGISTER, {
        method: 'POST',
        body: JSON.stringify(userData),
      });
      
      if (response.token) {
        setToken(response.token);
        setUser(response.user);
        localStorage.setItem('token', response.token);
        localStorage.setItem('refreshToken', response.refreshToken);
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const login = async (credentials) => {
    try {
      const response = await apiCall(API_ENDPOINTS.AUTH.LOGIN, {
        method: 'POST',
        body: JSON.stringify(credentials),
      });
      
      if (response.token) {
        setToken(response.token);
        setUser(response.user);
        localStorage.setItem('token', response.token);
        localStorage.setItem('refreshToken', response.refreshToken);
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  };

  const getCurrentUser = async () => {
    try {
      setLoading(true);
      const response = await apiCall(API_ENDPOINTS.AUTH.ME);
      setUser(response);
    } catch (error) {
      console.error('Failed to get current user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    apiCall,
    isAuthenticated: !!token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### 2.2 Wrap App with Auth Provider
Update `src/App.js`:

```javascript
// src/App.js
import React from 'react';
import { AuthProvider } from './context/AuthContext';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import { useAuth } from './context/AuthContext';

function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <Dashboard /> : <Login />;
}

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <AppContent />
      </div>
    </AuthProvider>
  );
}

export default App;
```

## 🔓 **Step 3: Authentication Components**

### 3.1 Login Component
Create `src/components/Login.js`:

```javascript
// src/components/Login.js
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login({
          username: formData.username,
          password: formData.password
        });
      } else {
        await register({
          username: formData.username,
          email: formData.email,
          password: formData.password
        });
      }
    } catch (error) {
      setError(error.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>{isLogin ? 'Login' : 'Register'}</h2>
        
        {error && <div className="error">{error}</div>}
        
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={formData.username}
          onChange={handleChange}
          required
        />
        
        {!isLogin && (
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        )}
        
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
        </button>
        
        <p>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            type="button" 
            onClick={() => setIsLogin(!isLogin)}
            className="link-button"
          >
            {isLogin ? 'Register' : 'Login'}
          </button>
        </p>
      </form>
    </div>
  );
};

export default Login;
```

## 📁 **Step 4: Portfolio Service Integration**

### 4.1 Portfolio API Service
Create `src/services/portfolioService.js`:

```javascript
// src/services/portfolioService.js
import { API_ENDPOINTS } from '../config/api';

export class PortfolioService {
  constructor(apiCall) {
    this.apiCall = apiCall;
  }

  // Get all projects with optional pagination
  async getProjects(page = 0, size = 10) {
    const url = `${API_ENDPOINTS.PORTFOLIO.PROJECTS}?page=${page}&size=${size}`;
    return await this.apiCall(url);
  }

  // Get project by ID
  async getProject(id) {
    return await this.apiCall(API_ENDPOINTS.PORTFOLIO.PROJECT_BY_ID(id));
  }

  // Create new project
  async createProject(projectData) {
    return await this.apiCall(API_ENDPOINTS.PORTFOLIO.PROJECTS, {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  }

  // Update existing project
  async updateProject(id, projectData) {
    return await this.apiCall(API_ENDPOINTS.PORTFOLIO.PROJECT_BY_ID(id), {
      method: 'PUT',
      body: JSON.stringify(projectData),
    });
  }

  // Delete project
  async deleteProject(id) {
    return await this.apiCall(API_ENDPOINTS.PORTFOLIO.PROJECT_BY_ID(id), {
      method: 'DELETE',
    });
  }

  // Get featured projects
  async getFeaturedProjects() {
    return await this.apiCall(API_ENDPOINTS.PORTFOLIO.FEATURED);
  }

  // Get projects by category
  async getProjectsByCategory(category) {
    return await this.apiCall(API_ENDPOINTS.PORTFOLIO.BY_CATEGORY(category));
  }
}
```

### 4.2 Portfolio Hook
Create `src/hooks/usePortfolio.js`:

```javascript
// src/hooks/usePortfolio.js
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { PortfolioService } from '../services/portfolioService';

export const usePortfolio = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { apiCall } = useAuth();
  
  const portfolioService = new PortfolioService(apiCall);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await portfolioService.getProjects();
      setProjects(response.content || response); // Handle paginated or simple array response
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (projectData) => {
    try {
      setError(null);
      const newProject = await portfolioService.createProject(projectData);
      setProjects(prev => [newProject, ...prev]);
      return newProject;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const updateProject = async (id, projectData) => {
    try {
      setError(null);
      const updatedProject = await portfolioService.updateProject(id, projectData);
      setProjects(prev => 
        prev.map(project => 
          project.id === id ? updatedProject : project
        )
      );
      return updatedProject;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const deleteProject = async (id) => {
    try {
      setError(null);
      await portfolioService.deleteProject(id);
      setProjects(prev => prev.filter(project => project.id !== id));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  return {
    projects,
    loading,
    error,
    loadProjects,
    createProject,
    updateProject,
    deleteProject,
  };
};
```

## 📊 **Step 5: Portfolio Components**

### 5.1 Projects List Component
Create `src/components/ProjectsList.js`:

```javascript
// src/components/ProjectsList.js
import React from 'react';
import { usePortfolio } from '../hooks/usePortfolio';

const ProjectsList = () => {
  const { projects, loading, error, deleteProject } = usePortfolio();

  if (loading) return <div>Loading projects...</div>;
  if (error) return <div>Error: {error}</div>;

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await deleteProject(id);
      } catch (error) {
        alert('Failed to delete project');
      }
    }
  };

  return (
    <div className="projects-list">
      <h2>My Projects</h2>
      {projects.length === 0 ? (
        <p>No projects found. Create your first project!</p>
      ) : (
        <div className="projects-grid">
          {projects.map(project => (
            <div key={project.id} className="project-card">
              {project.image && (
                <img 
                  src={project.image} 
                  alt={project.title}
                  className="project-image"
                />
              )}
              
              <div className="project-content">
                <h3>{project.title}</h3>
                <p>{project.description}</p>
                
                <div className="project-meta">
                  <span className="category">{project.category}</span>
                  <span className="year">{project.year}</span>
                  {project.featured && <span className="featured">⭐ Featured</span>}
                </div>
                
                <div className="technologies">
                  {project.technologies?.map((tech, index) => (
                    <span key={index} className="tech-tag">{tech}</span>
                  ))}
                </div>
                
                <div className="project-links">
                  {project.link && (
                    <a href={project.link} target="_blank" rel="noopener noreferrer">
                      View Live
                    </a>
                  )}
                  {project.github && (
                    <a href={project.github} target="_blank" rel="noopener noreferrer">
                      GitHub
                    </a>
                  )}
                </div>
                
                <div className="project-actions">
                  <button onClick={() => handleDelete(project.id)}>
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectsList;
```

### 5.2 Project Form Component
Create `src/components/ProjectForm.js`:

```javascript
// src/components/ProjectForm.js
import React, { useState } from 'react';
import { usePortfolio } from '../hooks/usePortfolio';

const ProjectForm = ({ project, onSuccess, onCancel }) => {
  const { createProject, updateProject } = usePortfolio();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: project?.title || '',
    description: project?.description || '',
    link: project?.link || '',
    github: project?.github || '',
    image: project?.image || '',
    technologies: project?.technologies?.join(', ') || '',
    status: project?.status || 'completed',
    category: project?.category || '',
    year: project?.year || new Date().getFullYear(),
    featured: project?.featured || false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const projectData = {
        ...formData,
        technologies: formData.technologies
          .split(',')
          .map(tech => tech.trim())
          .filter(tech => tech.length > 0),
        year: parseInt(formData.year),
      };

      if (project) {
        await updateProject(project.id, projectData);
      } else {
        await createProject(projectData);
      }

      onSuccess?.();
    } catch (error) {
      console.error('Failed to save project:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="project-form">
      <h3>{project ? 'Edit Project' : 'Create New Project'}</h3>
      
      <input
        type="text"
        name="title"
        placeholder="Project Title"
        value={formData.title}
        onChange={handleChange}
        required
      />
      
      <textarea
        name="description"
        placeholder="Project Description"
        value={formData.description}
        onChange={handleChange}
        rows={4}
        required
      />
      
      <input
        type="url"
        name="link"
        placeholder="Live Demo URL"
        value={formData.link}
        onChange={handleChange}
      />
      
      <input
        type="url"
        name="github"
        placeholder="GitHub Repository URL"
        value={formData.github}
        onChange={handleChange}
      />
      
      <input
        type="url"
        name="image"
        placeholder="Preview Image URL"
        value={formData.image}
        onChange={handleChange}
      />
      
      <input
        type="text"
        name="technologies"
        placeholder="Technologies (comma-separated)"
        value={formData.technologies}
        onChange={handleChange}
      />
      
      <select
        name="status"
        value={formData.status}
        onChange={handleChange}
        required
      >
        <option value="completed">Completed</option>
        <option value="in-progress">In Progress</option>
        <option value="planned">Planned</option>
      </select>
      
      <input
        type="text"
        name="category"
        placeholder="Category (e.g., Full-Stack Application)"
        value={formData.category}
        onChange={handleChange}
        required
      />
      
      <input
        type="number"
        name="year"
        placeholder="Year"
        value={formData.year}
        onChange={handleChange}
        min="2000"
        max="2030"
        required
      />
      
      <label>
        <input
          type="checkbox"
          name="featured"
          checked={formData.featured}
          onChange={handleChange}
        />
        Featured Project
      </label>
      
      <div className="form-actions">
        <button type="submit" disabled={loading}>
          {loading ? 'Saving...' : (project ? 'Update' : 'Create')}
        </button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
};

export default ProjectForm;
```

## 🎨 **Step 6: Main Dashboard Component**

Create `src/components/Dashboard.js`:

```javascript
// src/components/Dashboard.js
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import ProjectsList from './ProjectsList';
import ProjectForm from './ProjectForm';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome, {user?.username}</h1>
        <button onClick={logout}>Logout</button>
      </header>
      
      <main className="dashboard-content">
        <div className="dashboard-actions">
          <button 
            onClick={() => setShowForm(true)}
            className="create-project-btn"
          >
            Create New Project
          </button>
        </div>
        
        {showForm && (
          <div className="modal">
            <div className="modal-content">
              <ProjectForm
                onSuccess={() => setShowForm(false)}
                onCancel={() => setShowForm(false)}
              />
            </div>
          </div>
        )}
        
        <ProjectsList />
      </main>
    </div>
  );
};

export default Dashboard;
```

## 🎨 **Step 7: Basic Styling**

Create `src/App.css`:

```css
/* src/App.css */
.App {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Login Styles */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 1.5rem;
}

.login-form input {
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.login-form button {
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 8px 0;
}

.login-form button:hover {
  background: #0056b3;
}

.login-form button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin: 8px 0;
}

.link-button {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  text-decoration: underline;
}

/* Dashboard Styles */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.dashboard-actions {
  margin-bottom: 2rem;
}

.create-project-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
}

/* Projects Grid */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.project-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.project-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.project-content {
  padding: 1rem;
}

.project-meta {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
  font-size: 0.9rem;
}

.category {
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 4px;
}

.featured {
  background: #fff3cd;
  padding: 4px 8px;
  border-radius: 4px;
}

.technologies {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0;
}

.tech-tag {
  background: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.project-links a {
  display: inline-block;
  margin-right: 1rem;
  color: #007bff;
  text-decoration: none;
}

.project-links a:hover {
  text-decoration: underline;
}

/* Modal */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

/* Form Styles */
.project-form input,
.project-form textarea,
.project-form select {
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.form-actions button {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-actions button[type="submit"] {
  background: #007bff;
  color: white;
}

.form-actions button[type="button"] {
  background: #6c757d;
  color: white;
}
```

## 🚀 **Step 8: Usage Examples**

### 8.1 Complete Example App
Here's how your `src/App.js` should look:

```javascript
// src/App.js
import React from 'react';
import { AuthProvider } from './context/AuthContext';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import { useAuth } from './context/AuthContext';
import './App.css';

function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        Loading...
      </div>
    );
  }

  return isAuthenticated ? <Dashboard /> : <Login />;
}

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <AppContent />
      </div>
    </AuthProvider>
  );
}

export default App;
```

## 🔧 **Step 9: Advanced Features**

### 9.1 Error Boundary
Create `src/components/ErrorBoundary.js`:

```javascript
// src/components/ErrorBoundary.js
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>Something went wrong.</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

### 9.2 Loading Component
Create `src/components/Loading.js`:

```javascript
// src/components/Loading.js
import React from 'react';

const Loading = ({ message = 'Loading...' }) => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '2rem',
    flexDirection: 'column'
  }}>
    <div style={{
      width: '40px',
      height: '40px',
      border: '4px solid #f3f3f3',
      borderTop: '4px solid #007bff',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite'
    }}></div>
    <p style={{ marginTop: '1rem' }}>{message}</p>
    <style jsx>{`
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `}</style>
  </div>
);

export default Loading;
```

## 📱 **Step 10: Testing Your Integration**

### 10.1 Test Checklist
Before deploying your React app:

- ✅ Can register new users
- ✅ Can login existing users  
- ✅ Can view projects list
- ✅ Can create new projects
- ✅ Can edit existing projects
- ✅ Can delete projects
- ✅ Authentication persists on page refresh
- ✅ Proper error handling for network issues
- ✅ Loading states work correctly

### 10.2 Development vs Production
```javascript
// Development: Backend at localhost:8080
// Production: Backend at your Railway URL

// Make sure your CORS is configured properly in Spring Boot:
@CrossOrigin(origins = {
    "http://localhost:3000",      // React development
    "https://your-frontend.com"   // Your deployed frontend
})
```

## 🎯 **Next Steps**

1. **Add more features**: Search, filtering, pagination
2. **Improve UI**: Use a component library like Material-UI or Chakra UI
3. **Add file upload**: For project images
4. **Add real-time features**: WebSocket notifications
5. **Add testing**: Unit tests with Jest and React Testing Library
6. **Deploy frontend**: Netlify, Vercel, or GitHub Pages

## 📚 **Quick Reference**

### Common API Patterns
```javascript
// GET request
const projects = await apiCall('/api/portfolio/projects');

// POST request
const newProject = await apiCall('/api/portfolio/projects', {
  method: 'POST',
  body: JSON.stringify(projectData)
});

// PUT request  
const updated = await apiCall(`/api/portfolio/projects/${id}`, {
  method: 'PUT',
  body: JSON.stringify(updateData)
});

// DELETE request
await apiCall(`/api/portfolio/projects/${id}`, {
  method: 'DELETE'
});
```

### Environment Variables
```bash
# .env
REACT_APP_API_BASE_URL=http://localhost:8080

# .env.production
REACT_APP_API_BASE_URL=https://your-railway-app.railway.app
```

---

**🎉 You're all set!** Your React app is now fully integrated with your Spring Boot backend. You can authenticate users, manage portfolio projects, and everything works both locally and in production! 