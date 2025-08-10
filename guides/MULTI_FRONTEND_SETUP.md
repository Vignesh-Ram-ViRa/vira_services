# Multi-Frontend Setup Guide

> **How to connect multiple frontend applications to your centralized Vira Auth Service**

## 🎯 **Overview**

Your Vira Services backend is designed as a **centralized authentication service** that can serve multiple frontend applications simultaneously. This guide shows you how to:

- Connect multiple React/Vue/Angular apps to the same auth service
- Configure CORS for development and production
- Share user sessions across different applications
- Manage users from a single dashboard

---

## 🌐 **CORS Configuration**

### **Pre-configured Development URLs (Automatic)**

Your auth service automatically accepts requests from these development URLs:

```yaml
Development URLs (No setup required):
- http://localhost:3000      # React default
- http://localhost:3001      # Second React app  
- http://localhost:5173      # Vite default
- http://localhost:8080      # Spring Boot, Vue CLI
- http://127.0.0.1:3000      # Alternative localhost
- http://127.0.0.1:5173      # Alternative Vite
```

**This means:** You can start developing immediately on any of these ports without additional configuration.

### **Production URLs (Environment Variables)**

For production deployments, configure these environment variables in Render:

```bash
FRONTEND_URL_1=https://your-portfolio.netlify.app
FRONTEND_URL_2=https://your-business-app.vercel.app  
FRONTEND_URL_3=https://your-third-app.com
FRONTEND_URL_4=https://your-fourth-app.com
FRONTEND_URL_5=https://your-fifth-app.com
```

---

## 🚀 **Adding New Frontend Applications**

### **Step 1: Deploy Your Frontend**

Deploy your frontend to any hosting platform:
- **Netlify**: `https://your-app.netlify.app`
- **Vercel**: `https://your-app.vercel.app`
- **GitHub Pages**: `https://username.github.io/repo-name`
- **Custom Domain**: `https://your-custom-domain.com`

### **Step 2: Update Environment Variables**

1. **Go to Render Dashboard**
   - Navigate to your `vira-services` web service
   - Click **"Environment"** tab

2. **Add/Update Frontend URL**
   - Set any available `FRONTEND_URL_X` to your new frontend URL
   - Example: `FRONTEND_URL_2=https://my-new-app.netlify.app`

3. **Save and Redeploy**
   - Click **"Save Changes"**
   - Render automatically redeploys with new CORS settings
   - Takes ~3-5 minutes

### **Step 3: Configure Your Frontend**

Update your frontend to use the centralized auth service:

```javascript
// config/api.js
export const API_CONFIG = {
  BASE_URL: 'https://vira-services-xxxx.onrender.com/api',
  AUTH_ENDPOINTS: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/profile',
    REFRESH: '/auth/refresh'
  }
};
```

---

## 📱 **Frontend Integration Examples**

### **React Example**

```javascript
// services/authService.js
const API_BASE = 'https://vira-services-xxxx.onrender.com/api';

class AuthService {
  async login(username, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Important for cookies
      body: JSON.stringify({ username, password })
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    
    // Store JWT token
    localStorage.setItem('authToken', data.accessToken);
    localStorage.setItem('refreshToken', data.refreshToken);
    
    return data;
  }

  async register(username, email, password) {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ username, email, password })
    });
    
    if (!response.ok) {
      throw new Error('Registration failed');
    }
    
    return response.json();
  }

  async getProfile() {
    const token = localStorage.getItem('authToken');
    
    const response = await fetch(`${API_BASE}/auth/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get profile');
    }
    
    return response.json();
  }

  async logout() {
    const token = localStorage.getItem('authToken');
    
    await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      credentials: 'include'
    });
    
    // Clear local storage
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
  }

  isAuthenticated() {
    return !!localStorage.getItem('authToken');
  }

  getToken() {
    return localStorage.getItem('authToken');
  }
}

export default new AuthService();
```

### **Vue.js Example**

```javascript
// services/auth.js
import axios from 'axios';

const API_BASE = 'https://vira-services-xxxx.onrender.com/api';

// Configure axios defaults
axios.defaults.baseURL = API_BASE;
axios.defaults.withCredentials = true;

// Add token to requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  async login(username, password) {
    const response = await axios.post('/auth/login', {
      username,
      password
    });
    
    localStorage.setItem('authToken', response.data.accessToken);
    localStorage.setItem('refreshToken', response.data.refreshToken);
    
    return response.data;
  },

  async register(username, email, password) {
    const response = await axios.post('/auth/register', {
      username,
      email,
      password
    });
    
    return response.data;
  },

  async getProfile() {
    const response = await axios.get('/auth/profile');
    return response.data;
  },

  async logout() {
    await axios.post('/auth/logout');
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
  },

  isAuthenticated() {
    return !!localStorage.getItem('authToken');
  }
};
```

### **Angular Example**

```typescript
// services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiBase = 'https://vira-services-xxxx.onrender.com/api';

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.apiBase}/auth/login`, {
      username,
      password
    }, {
      withCredentials: true
    });
  }

  register(username: string, email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiBase}/auth/register`, {
      username,
      email,
      password
    }, {
      withCredentials: true
    });
  }

  getProfile(): Observable<any> {
    const token = localStorage.getItem('authToken');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.get(`${this.apiBase}/auth/profile`, {
      headers,
      withCredentials: true
    });
  }

  logout(): Observable<any> {
    const token = localStorage.getItem('authToken');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.post(`${this.apiBase}/auth/logout`, {}, {
      headers,
      withCredentials: true
    });
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('authToken');
  }

  storeTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('authToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
  }

  clearTokens(): void {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
  }
}
```

---

## 🔐 **Shared Authentication Across Apps**

### **JWT Token Sharing**

Since all your frontend applications use the same auth service, users can:

1. **Login once** in any application
2. **Use the same JWT token** across all your applications
3. **Stay logged in** when switching between applications
4. **Logout from any app** affects all applications

### **Cross-Application User Sessions**

```javascript
// Shared utility for cross-app authentication
class SharedAuth {
  constructor() {
    this.authService = 'https://vira-services-xxxx.onrender.com/api';
    this.storageKey = 'vira_auth_token';
  }

  // Check if user is logged in across all apps
  isGloballyAuthenticated() {
    const token = localStorage.getItem(this.storageKey);
    return token && !this.isTokenExpired(token);
  }

  // Get user info (works for all apps)
  async getGlobalUser() {
    const token = localStorage.getItem(this.storageKey);
    if (!token) return null;

    try {
      const response = await fetch(`${this.authService}/auth/profile`, {
        headers: { 'Authorization': `Bearer ${token}` },
        credentials: 'include'
      });
      
      if (response.ok) {
        return response.json();
      }
    } catch (error) {
      console.error('Failed to get global user:', error);
    }
    
    return null;
  }

  // Global logout (affects all apps)
  async globalLogout() {
    const token = localStorage.getItem(this.storageKey);
    if (token) {
      try {
        await fetch(`${this.authService}/auth/logout`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          credentials: 'include'
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    
    localStorage.removeItem(this.storageKey);
    localStorage.removeItem('vira_refresh_token');
  }

  isTokenExpired(token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp < Date.now() / 1000;
    } catch {
      return true;
    }
  }
}

// Use across all your applications
export const sharedAuth = new SharedAuth();
```

---

## 🗄️ **User Management**

### **Centralized User Dashboard**

Manage all users across all your applications from:

1. **Supabase Dashboard**
   - Go to: `https://app.supabase.com/project/your-project-ref`
   - Navigate to **Table Editor** → **auth_users**
   - View, edit, delete users
   - See which users are active across all applications

2. **API Endpoints** (for admin operations)
   ```javascript
   // Admin endpoints (requires ADMIN role)
   GET /api/admin/users          // List all users
   PUT /api/admin/users/{id}/role // Change user role
   DELETE /api/admin/users/{id}   // Delete user
   ```

### **User Analytics Across Apps**

Track user activity across all your applications:

```sql
-- Query active users across all applications
SELECT 
  u.username,
  u.email,
  u.created_at,
  u.last_login,
  COUNT(rt.id) as active_sessions
FROM auth_users u
LEFT JOIN auth_refresh_tokens rt ON u.id = rt.user_id
WHERE rt.expires_at > NOW()
GROUP BY u.id
ORDER BY u.last_login DESC;
```

---

## 🚀 **Deployment Workflow**

### **Adding a New Frontend Application:**

1. **Develop Locally**
   - Use any `localhost:XXXX` port (automatically allowed)
   - Integrate with auth service using examples above
   - Test login/logout/registration

2. **Deploy to Production**
   - Deploy to Netlify/Vercel/etc.
   - Get production URL (e.g., `https://my-app.netlify.app`)

3. **Update Auth Service**
   - Add URL to environment variables in Render
   - Service auto-redeploys with new CORS settings

4. **Test Production**
   - Verify CORS works
   - Test authentication flows
   - Confirm shared sessions work

### **Zero Downtime Updates**

- **Frontend updates**: Deploy independently, no backend changes needed
- **Backend updates**: All frontends continue working
- **CORS updates**: Automatic redeployment, ~3-5 minutes downtime

---

## 🎯 **Use Case Examples**

### **Portfolio + Business Website**
```
Portfolio App (React):     https://johndoe.dev
Business App (Vue):        https://johndoe-consulting.com
Admin Dashboard (Angular): https://admin.johndoe.com

Shared Auth: https://vira-services-xxxx.onrender.com
```

### **E-commerce + Blog + Docs**
```
Store Front (Next.js):     https://mystore.com
Blog (Gatsby):             https://blog.mystore.com  
Documentation (VuePress):  https://docs.mystore.com

Shared Auth: https://vira-services-xxxx.onrender.com
```

### **Client Projects**
```
Client A Portfolio:        https://client-a.netlify.app
Client B Business App:     https://client-b.vercel.app
Client C Landing Page:     https://client-c.github.io

Shared Auth: https://vira-services-xxxx.onrender.com
```

---

## 📋 **Environment Variable Template**

Copy this template for your Render environment variables:

```bash
# Authentication & Security
SPRING_PROFILES_ACTIVE=prod
JWT_SECRET=YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=
ADMIN_PASSWORD=SecureAdmin123!

# Frontend Applications (update as you deploy)
FRONTEND_URL_1=https://my-portfolio.netlify.app
FRONTEND_URL_2=https://my-business.vercel.app
FRONTEND_URL_3=https://my-blog.github.io
FRONTEND_URL_4=https://my-docs.surge.sh
FRONTEND_URL_5=https://my-landing.firebase.app

# Supabase Database
SUPABASE_DATABASE_URL=postgresql://postgres.abc123:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
SUPABASE_DATABASE_USERNAME=postgres.abc123
SUPABASE_DATABASE_PASSWORD=your-supabase-password
```

---

## 🎉 **Benefits Summary**

✅ **Single Auth Service** - One backend serves unlimited frontends  
✅ **Shared User Base** - Users work across all your applications  
✅ **Centralized Management** - Manage all users from one dashboard  
✅ **Independent Deployment** - Deploy frontends without backend changes  
✅ **Cross-App Sessions** - Login once, authenticated everywhere  
✅ **Scalable Architecture** - Add new apps without limit  
✅ **Zero Maintenance** - Backend never requires monthly tasks  
✅ **$0 Cost** - Free for personal/small business use  

**Your centralized auth service is ready to power unlimited frontend applications!** 🚀 