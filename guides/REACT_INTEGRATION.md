# React Integration Guide

> **Complete guide to integrate React applications with Vira Services backend including role-based UI components**

## 🎯 **Overview**

This guide covers:
- **Authentication Setup** with JWT tokens
- **Google OAuth Integration** for seamless login
- **Guest Access** for public content viewing
- **Role-Based UI Components** (ADMIN, SUPER_USER, NORMAL_USER, GUEST)
- **API Service Layer** for backend communication
- **Protected Routes** and navigation
- **Complete Examples** ready to use

## 🚀 **Quick Setup**

### Prerequisites
- React application (Create React App, Next.js, Vite)
- Axios or fetch for API calls
- React Router for navigation

### Install Dependencies
```bash
npm install axios react-router-dom
# For Google OAuth (optional)
npm install react-google-login
# Optional: Context API (built-in) or state management library
```

## 🔐 **Authentication Setup**

### 1. Auth Context (React Context API)

**`src/contexts/AuthContext.js`:**
```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Initialize auth state
  useEffect(() => {
    if (token) {
      getCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const getCurrentUser = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      console.error('Failed to get current user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    const response = await authAPI.login(credentials);
    const { token: newToken, user: userData } = response.data;
    
    setToken(newToken);
    setUser(userData);
    localStorage.setItem('token', newToken);
    
    return response;
  };

  const register = async (userData) => {
    const response = await authAPI.register(userData);
    const { token: newToken, user: newUser } = response.data;
    
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem('token', newToken);
    
    return response;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  // Role checking functions
  const hasRole = (role) => {
    return user?.roles?.includes(role) || false;
  };

  const hasAnyRole = (roles) => {
    return roles.some(role => hasRole(role));
  };

  const isAdmin = () => hasRole('ADMIN');
  const isSuperUser = () => hasRole('SUPER_USER');
  const isNormalUser = () => hasRole('NORMAL_USER');
  const isAuthenticated = () => !!user && !!token;

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    hasRole,
    hasAnyRole,
    isAdmin,
    isSuperUser,
    isNormalUser,
    isAuthenticated,
    getCurrentUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### 2. API Service Layer

**`src/services/api.js`:**
```javascript
import axios from 'axios';

// Configure base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  registerSuperUser: (userData) => api.post('/api/auth/register-super-user', userData),
  logout: () => api.post('/api/auth/logout'),
  getCurrentUser: () => api.get('/api/auth/me'),
  refreshToken: (refreshToken) => api.post('/api/auth/refresh', { refreshToken }),
};

// Google OAuth (No token required)
export const oauthAPI = {
  // Redirect to Google OAuth (use window.location.href)
  googleLogin: () => `${API_BASE_URL}/oauth2/authorization/google`,
};

// Public/Guest API (No authentication required)
export const publicAPI = {
  getPublicProjects: (params) => axios.get(`${API_BASE_URL}/api/public/projects`, { params }),
  getPublicProjectById: (id) => axios.get(`${API_BASE_URL}/api/public/projects/${id}`),
  getFeaturedProjects: () => axios.get(`${API_BASE_URL}/api/public/projects/featured`),
  getProjectStats: () => axios.get(`${API_BASE_URL}/api/public/projects/stats`),
  getProjectTechnologies: () => axios.get(`${API_BASE_URL}/api/public/technologies`),
};

// Admin API
export const adminAPI = {
  getPendingApprovals: () => api.get('/api/admin/pending-approvals'),
  approveSuperUser: (approvalData) => api.post('/api/admin/approve-super-user', approvalData),
  updateUserRole: (userId, role) => api.put(`/api/admin/users/${userId}/role?role=${role}`),
  registerSuperUserDirect: (userData) => api.post('/api/admin/register-super-user', userData),
};

// Portfolio API
export const portfolioAPI = {
  getProjects: (params) => api.get('/api/portfolio/projects', { params }),
  getProject: (id) => api.get(`/api/portfolio/projects/${id}`),
  createProject: (projectData) => api.post('/api/portfolio/projects', projectData),
  updateProject: (id, projectData) => api.put(`/api/portfolio/projects/${id}`, projectData),
  deleteProject: (id) => api.delete(`/api/portfolio/projects/${id}`),
  getProjectStats: () => api.get('/api/portfolio/projects/stats'),
};

export default api;
```

## 🛡️ **Role-Based UI Components**

### 1. Role Guard Component

**`src/components/auth/RoleGuard.jsx`:**
```javascript
import { useAuth } from '../../contexts/AuthContext';

const RoleGuard = ({ 
  allowedRoles, 
  children, 
  fallback = null,
  requireAuth = true 
}) => {
  const { hasAnyRole, isAuthenticated } = useAuth();

  // Check authentication requirement
  if (requireAuth && !isAuthenticated()) {
    return fallback || <div>Please log in to access this content.</div>;
  }

  // Check role requirements
  if (allowedRoles && allowedRoles.length > 0) {
    if (!hasAnyRole(allowedRoles)) {
      return fallback || <div>You don't have permission to access this content.</div>;
    }
  }

  return children;
};

export default RoleGuard;
```

### 2. Specific Role Components

**`src/components/auth/RoleComponents.jsx`:**
```javascript
import { useAuth } from '../../contexts/AuthContext';
import RoleGuard from './RoleGuard';

// Admin Only Component
export const AdminOnly = ({ children, fallback }) => (
  <RoleGuard allowedRoles={['ADMIN']} fallback={fallback}>
    {children}
  </RoleGuard>
);

// Super User and Admin
export const SuperUserOnly = ({ children, fallback }) => (
  <RoleGuard allowedRoles={['ADMIN', 'SUPER_USER']} fallback={fallback}>
    {children}
  </RoleGuard>
);

// Authenticated Users (Normal, Super, Admin)
export const AuthenticatedOnly = ({ children, fallback }) => (
  <RoleGuard allowedRoles={['NORMAL_USER', 'SUPER_USER', 'ADMIN']} fallback={fallback}>
    {children}
  </RoleGuard>
);

// Guest Access (anyone, including unauthenticated)
export const GuestAccess = ({ children }) => {
  return children; // No restrictions
};

// Conditional role rendering
export const RoleBasedRender = ({ children }) => {
  const { hasRole, isAuthenticated } = useAuth();

  return (
    <>
      {/* Admin Content */}
      {hasRole('ADMIN') && (
        <div className="admin-content">
          {children.admin}
        </div>
      )}

      {/* Super User Content */}
      {hasRole('SUPER_USER') && (
        <div className="super-user-content">
          {children.superUser}
        </div>
      )}

      {/* Normal User Content */}
      {hasRole('NORMAL_USER') && (
        <div className="normal-user-content">
          {children.normalUser}
        </div>
      )}

      {/* Guest Content */}
      {!isAuthenticated() && (
        <div className="guest-content">
          {children.guest}
        </div>
      )}
    </>
  );
};
```

## 🔄 **Authentication Components**

### 1. Login Component

**`src/components/auth/Login.jsx`:**
```javascript
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(formData);
      navigate('/dashboard');
    } catch (error) {
      setError(error.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

### 2. Registration Choice Component

**`src/components/auth/RegistrationChoice.jsx`:**
```javascript
import React from 'react';
import { Link } from 'react-router-dom';

const RegistrationChoice = () => {
  return (
    <div className="registration-choice">
      <h2>Choose Registration Type</h2>
      
      <div className="registration-options">
        <div className="option-card">
          <h3>Normal User</h3>
          <p>Standard access to manage your own projects and data</p>
          <ul>
            <li>Create and manage portfolios</li>
            <li>Personal project tracking</li>
            <li>Standard features</li>
          </ul>
          <Link to="/register" className="btn btn-primary">
            Register as Normal User
          </Link>
        </div>

        <div className="option-card">
          <h3>Super User</h3>
          <p>Read-only access to all data (requires admin approval)</p>
          <ul>
            <li>View all projects and analytics</li>
            <li>Business reporting access</li>
            <li>Requires admin approval</li>
          </ul>
          <Link to="/register-super-user" className="btn btn-secondary">
            Request Super User Access
          </Link>
        </div>

        <div className="option-card">
          <h3>Continue as Guest</h3>
          <p>Limited access to public content</p>
          <ul>
            <li>View public projects</li>
            <li>Limited features</li>
            <li>No account required</li>
          </ul>
          <Link to="/guest" className="btn btn-outline">
            Continue as Guest
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegistrationChoice;
```

## 🎛️ **Admin Panel Components**

### 1. Admin Dashboard

**`src/components/admin/AdminDashboard.jsx`:**
```javascript
import React from 'react';
import { AdminOnly } from '../auth/RoleComponents';
import SuperUserApprovals from './SuperUserApprovals';
import UserRoleManager from './UserRoleManager';

const AdminDashboard = () => {
  return (
    <AdminOnly fallback={<div>Access denied. Admin role required.</div>}>
      <div className="admin-dashboard">
        <h1>Admin Dashboard</h1>
        
        <div className="admin-sections">
          <section className="approvals-section">
            <h2>Pending Approvals</h2>
            <SuperUserApprovals />
          </section>

          <section className="user-management-section">
            <h2>User Management</h2>
            <UserRoleManager />
          </section>
        </div>
      </div>
    </AdminOnly>
  );
};

export default AdminDashboard;
```

### 2. Super User Approvals Component

**`src/components/admin/SuperUserApprovals.jsx`:**
```javascript
import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';

const SuperUserApprovals = () => {
  const [pendingUsers, setPendingUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPendingApprovals();
  }, []);

  const fetchPendingApprovals = async () => {
    try {
      const response = await adminAPI.getPendingApprovals();
      setPendingUsers(response.data.data);
    } catch (error) {
      console.error('Failed to fetch pending approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (userId, approved, notes = '') => {
    try {
      await adminAPI.approveSuperUser({
        userId,
        approved,
        notes
      });
      
      // Refresh the list
      fetchPendingApprovals();
      
      alert(`User ${approved ? 'approved' : 'rejected'} successfully`);
    } catch (error) {
      console.error('Failed to process approval:', error);
      alert('Failed to process approval');
    }
  };

  if (loading) return <div>Loading pending approvals...</div>;

  if (pendingUsers.length === 0) {
    return <div>No pending approvals</div>;
  }

  return (
    <div className="super-user-approvals">
      <h3>Super User Approval Requests</h3>
      
      {pendingUsers.map(user => (
        <div key={user.id} className="approval-card">
          <div className="user-info">
            <h4>{user.username}</h4>
            <p>Email: {user.email}</p>
            <p>Requested Role: {user.requestedRole}</p>
            {user.approvalNotes && (
              <div className="approval-notes">
                <strong>Justification:</strong>
                <p>{user.approvalNotes}</p>
              </div>
            )}
          </div>
          
          <div className="approval-actions">
            <button 
              onClick={() => handleApproval(user.id, true, 'Approved by admin')}
              className="btn btn-success"
            >
              Approve
            </button>
            <button 
              onClick={() => handleApproval(user.id, false, 'Rejected by admin')}
              className="btn btn-danger"
            >
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SuperUserApprovals;
```

## 🚦 **Protected Routes**

### Route Protection Setup

**`src/components/routing/ProtectedRoute.jsx`:**
```javascript
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const ProtectedRoute = ({ children, allowedRoles = [], requireAuth = true }) => {
  const { isAuthenticated, hasAnyRole, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div>Loading...</div>;
  }

  // Check authentication requirement
  if (requireAuth && !isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role requirements
  if (allowedRoles.length > 0 && !hasAnyRole(allowedRoles)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### App Routing Example

**`src/App.js`:**
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/routing/ProtectedRoute';
import Navigation from './components/navigation/Navigation';

// Components
import Home from './pages/Home';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import AdminDashboard from './components/admin/AdminDashboard';
import SuperUserApprovals from './components/admin/SuperUserApprovals';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navigation />
          
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected routes for authenticated users */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute allowedRoles={['NORMAL_USER', 'SUPER_USER', 'ADMIN']}>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/portfolio"
              element={
                <ProtectedRoute allowedRoles={['NORMAL_USER', 'SUPER_USER', 'ADMIN']}>
                  <Portfolio />
                </ProtectedRoute>
              }
            />

            {/* Admin only routes */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={['ADMIN']}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />

            {/* Super User and Admin routes */}
            <Route
              path="/analytics"
              element={
                <ProtectedRoute allowedRoles={['SUPER_USER', 'ADMIN']}>
                  <AnalyticsView />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

## 🧭 **Navigation with Role-Based Menus**

**`src/components/navigation/Navigation.jsx`:**
```javascript
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Navigation = () => {
  const { 
    isAuthenticated, 
    hasRole, 
    user, 
    logout 
  } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <Link to="/">Vira Services</Link>
      </div>

      <div className="nav-links">
        {/* Public links */}
        <Link to="/">Home</Link>

        {/* Authenticated user links */}
        {isAuthenticated() && (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/portfolio">Portfolio</Link>
          </>
        )}

        {/* Super User and Admin links */}
        {hasRole('SUPER_USER') && (
          <Link to="/analytics">Analytics</Link>
        )}

        {/* Admin only links */}
        {hasRole('ADMIN') && (
          <>
            <Link to="/admin">Admin Panel</Link>
            <Link to="/admin/approvals">Approvals</Link>
          </>
        )}
      </div>

      <div className="nav-user">
        {isAuthenticated() ? (
          <div className="user-menu">
            <span>Welcome, {user?.username}</span>
            <span className="user-role">({user?.roles?.join(', ')})</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <div className="auth-links">
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
```

## 🔧 **Environment Configuration**

### Development vs Production

**`.env.development`:**
```bash
REACT_APP_API_URL=http://localhost:8080
REACT_APP_ENV=development
```

**`.env.production`:**
```bash
REACT_APP_API_URL=https://your-backend.railway.app
REACT_APP_ENV=production
```

## 🎯 **Usage Examples**

### Using Role Guards in Components

```javascript
import { RoleGuard, AdminOnly, SuperUserOnly } from '../components/auth/RoleComponents';

const ExamplePage = () => {
  return (
    <div>
      {/* Content for all authenticated users */}
      <RoleGuard allowedRoles={['NORMAL_USER', 'SUPER_USER', 'ADMIN']}>
        <UserDashboard />
      </RoleGuard>

      {/* Admin only content */}
      <AdminOnly>
        <AdminPanel />
      </AdminOnly>

      {/* Super User and Admin content */}
      <SuperUserOnly>
        <AnalyticsView />
      </SuperUserOnly>

      {/* Custom role combination */}
      <RoleGuard 
        allowedRoles={['ADMIN']} 
        fallback={<div>Admin access required</div>}
      >
        <SystemSettings />
      </RoleGuard>
    </div>
  );
};
```

### API Calls with Error Handling

```javascript
const ProjectComponent = () => {
  const [projects, setProjects] = useState([]);
  
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await portfolioAPI.getProjects({
          page: 0,
          size: 10,
          sortBy: 'createdAt',
          sortDir: 'desc'
        });
        setProjects(response.data.data.content);
      } catch (error) {
        console.error('Failed to fetch projects:', error);
        // Handle error (show notification, etc.)
      }
    };

    fetchProjects();
  }, []);

  // Component JSX...
};
```

## ✅ **Integration Checklist**

### Setup
- [ ] Auth context configured
- [ ] API service layer implemented
- [ ] Role guard components created
- [ ] Protected routes setup
- [ ] Navigation with role-based menus

### Security
- [ ] JWT tokens handled securely
- [ ] Frontend role checks for UX only
- [ ] API interceptors for auth headers
- [ ] Error handling for 401/403 responses
- [ ] Logout on token expiration

### User Experience
- [ ] Loading states implemented
- [ ] Error messages displayed
- [ ] Role-based content visibility
- [ ] Smooth navigation flows
- [ ] Registration type choices

### Testing
- [ ] Login/logout functionality
- [ ] Role-based component rendering
- [ ] Protected route access
- [ ] API calls with different roles
- [ ] Error scenarios handled

## 🔗 **Related Guides**

- **Backend Setup**: `guides/LOCAL_SETUP.md`
- **Deployment**: `guides/DEPLOYMENT.md`
- **Role Management**: `guides/ROLE_MANAGEMENT.md`
- **Security**: `guides/SECURITY.md`

---

**🎉 Your React app is now fully integrated with role-based authentication!** Start building amazing user experiences! 🚀 